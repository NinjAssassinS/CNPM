import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.drugs import Drugs
from services.openfda import OpenFDAService

logger = logging.getLogger(__name__)


class DrugsService:
    """Service layer for Drugs - checks local DB first, then falls back to OpenFDA API."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.fda = OpenFDAService()

    def _get_local(self):
        if not self.db:
            return None
        from services.local_drugs import LocalDrugsService
        return LocalDrugsService(self.db)

    def get_by_id(self, obj_id: int) -> Optional[Drugs]:
        """Get drug by ID from local database."""
        try:
            query = select(Drugs).where(Drugs.id == obj_id)
            result = self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching drug {obj_id}: {str(e)}")
            raise

    def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of drugs from local database."""
        try:
            query = select(Drugs)
            count_query = select(func.count(Drugs.id))

            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Drugs, field):
                        query = query.where(getattr(Drugs, field) == value)
                        count_query = count_query.where(getattr(Drugs, field) == value)

            total = self.db.execute(count_query).scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Drugs, field_name):
                        query = query.order_by(getattr(Drugs, field_name).desc())
                else:
                    if hasattr(Drugs, sort):
                        query = query.order_by(getattr(Drugs, sort))
            else:
                query = query.order_by(Drugs.id.desc())

            result = self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching drugs list: {str(e)}")
            raise

    async def search_by_name(self, query: str = "", limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        local = self._get_local()
        if local:
            result = local.search_by_name(query, skip=skip, limit=limit)
            if result.get("items"):
                return result

        try:
            result = await self.fda.search_drug_label(
                search=f"openfda.brand_name:{query} OR openfda.generic_name:{query}",
                limit=limit, skip=skip,
            )
            if result.get("error"):
                return {"items": [], "total": 0, "skip": skip, "limit": limit}
            items = [self._format_fda(r) for r in result.get("results", [])]
            return {
                "items": items,
                "total": result.get("meta", {}).get("results", {}).get("total", len(items)),
                "skip": skip, "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error searching drugs from FDA: {str(e)}")
            return {"items": [], "total": 0, "skip": skip, "limit": limit}

    async def get_by_generic_name(self, generic_name: str) -> Optional[Dict[str, Any]]:
        local = self._get_local()
        if local:
            drug = local.get_by_generic_name(generic_name)
            if drug:
                return drug

        try:
            result = await self.fda.get_drug_label_by_generic(generic_name, limit=1)
            if result.get("error") or not result.get("results"):
                return None
            return self._format_fda(result["results"][0])
        except Exception as e:
            logger.error(f"Error fetching drug {generic_name}: {str(e)}")
            return None

    async def get_enriched(self, brand_name: str = "", generic_name: str = "") -> Dict[str, Any]:
        return await self.fda.enrich_drug_info(brand_name=brand_name, generic_name=generic_name)

    def _format_fda(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        openfda = raw.get("openfda") or {}
        brand = (openfda.get("brand_name") or [None])[0]
        generic = (openfda.get("generic_name") or [None])[0]
        mfr = (openfda.get("manufacturer_name") or [None])[0]

        return {
            "id": (openfda.get("spl_id") or [None])[0] or hash(brand or generic or ""),
            "code": (openfda.get("product_ndc") or [None])[0] or "",
            "name": brand or generic or "Unknown",
            "generic_name": generic or "",
            "group_name": "FDA",
            "manufacturer": mfr or "FDA",
            "status": "active",
            "rating": 0,
            "price": "",
            "component": generic or "",
            "usage_info": (raw.get("indications_and_usage") or [""])[0] or (raw.get("purpose") or [""])[0] or "",
            "dosage": (raw.get("dosage_and_administration") or [""])[0] or "",
            "side_effects": (raw.get("adverse_reactions") or [""])[0] or "",
            "contraindications": (raw.get("contraindications") or [""])[0] or "",
            "data_source": "openfda",
            "fda_data": {
                "label": self.fda._extract_label_summary(raw) if hasattr(self.fda, '_extract_label_summary') else {},
            },
        }
