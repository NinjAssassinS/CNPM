import logging
from typing import Dict, Any, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.drugs import Drugs

logger = logging.getLogger(__name__)


class LocalDrugsService:
    """Service layer for querying drugs from the local database."""

    def __init__(self, db: Session):
        self.db = db

    def search_by_name(self, query: str = "", skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        try:
            base_query = select(Drugs)
            count_query = select(func.count(Drugs.id))

            if query:
                like = f"%{query}%"
                base_query = base_query.where(
                    Drugs.name.ilike(like) | Drugs.code.ilike(like) | Drugs.component.ilike(like)
                )
                count_query = count_query.where(
                    Drugs.name.ilike(like) | Drugs.code.ilike(like) | Drugs.component.ilike(like)
                )

            total = self.db.execute(count_query).scalar()
            result = self.db.execute(base_query.offset(skip).limit(limit).order_by(Drugs.name))
            items = [self._format(d) for d in result.scalars().all()]

            return {"items": items, "total": total, "skip": skip, "limit": limit}
        except Exception as e:
            logger.error(f"Error searching local drugs: {str(e)}")
            return {"items": [], "total": 0, "skip": skip, "limit": limit}

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            drug = self.db.execute(select(Drugs).where(Drugs.name.ilike(name))).scalar_one_or_none()
            return self._format(drug) if drug else None
        except Exception as e:
            logger.error(f"Error fetching local drug by name {name}: {str(e)}")
            return None

    def get_by_generic_name(self, generic_name: str) -> Optional[Dict[str, Any]]:
        try:
            pattern = f"%{generic_name}%"
            drug = self.db.execute(
                select(Drugs).where(Drugs.component.ilike(pattern) | Drugs.name.ilike(pattern))
            ).scalar_one_or_none()
            return self._format(drug) if drug else None
        except Exception as e:
            logger.error(f"Error fetching local drug by generic name {generic_name}: {str(e)}")
            return None

    def _format(self, drug: Drugs) -> Dict[str, Any]:
        return {
            "id": drug.id,
            "code": drug.code or "",
            "name": drug.name,
            "generic_name": drug.component or drug.name,
            "group_name": drug.group_name,
            "manufacturer": drug.manufacturer,
            "status": drug.status,
            "rating": drug.rating or 0,
            "price": drug.price or "",
            "component": drug.component or "",
            "usage_info": drug.usage_info or "",
            "dosage": drug.dosage or "",
            "side_effects": drug.side_effects or "",
            "contraindications": drug.contraindications or "",
            "data_source": "local",
        }
