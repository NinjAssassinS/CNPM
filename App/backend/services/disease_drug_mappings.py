import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.disease_drug_mappings import Disease_drug_mappings

logger = logging.getLogger(__name__)


class Disease_drug_mappingsService:
    """Service layer for Disease_drug_mappings operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: Dict[str, Any]) -> Optional[Disease_drug_mappings]:
        try:
            obj = Disease_drug_mappings(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Created disease_drug_mappings with id: {obj.id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating disease_drug_mappings: {str(e)}")
            raise

    def get_by_id(self, obj_id: int) -> Optional[Disease_drug_mappings]:
        try:
            query = select(Disease_drug_mappings).where(Disease_drug_mappings.id == obj_id)
            result = self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching disease_drug_mappings {obj_id}: {str(e)}")
            raise

    def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            query = select(Disease_drug_mappings)
            count_query = select(func.count(Disease_drug_mappings.id))
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Disease_drug_mappings, field):
                        query = query.where(getattr(Disease_drug_mappings, field) == value)
                        count_query = count_query.where(getattr(Disease_drug_mappings, field) == value)
            
            count_result = self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Disease_drug_mappings, field_name):
                        query = query.order_by(getattr(Disease_drug_mappings, field_name).desc())
                else:
                    if hasattr(Disease_drug_mappings, sort):
                        query = query.order_by(getattr(Disease_drug_mappings, sort))
            else:
                query = query.order_by(Disease_drug_mappings.id.desc())

            result = self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching disease_drug_mappings list: {str(e)}")
            raise

    def update(self, obj_id: int, update_data: Dict[str, Any]) -> Optional[Disease_drug_mappings]:
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Disease_drug_mappings {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            self.db.commit()
            self.db.refresh(obj)
            logger.info(f"Updated disease_drug_mappings {obj_id}")
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating disease_drug_mappings {obj_id}: {str(e)}")
            raise

    def delete(self, obj_id: int) -> bool:
        try:
            obj = self.get_by_id(obj_id)
            if not obj:
                logger.warning(f"Disease_drug_mappings {obj_id} not found for deletion")
                return False
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"Deleted disease_drug_mappings {obj_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting disease_drug_mappings {obj_id}: {str(e)}")
            raise

    def get_by_field(self, field_name: str, field_value: Any) -> Optional[Disease_drug_mappings]:
        try:
            if not hasattr(Disease_drug_mappings, field_name):
                raise ValueError(f"Field {field_name} does not exist on Disease_drug_mappings")
            result = self.db.execute(
                select(Disease_drug_mappings).where(getattr(Disease_drug_mappings, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching disease_drug_mappings by {field_name}: {str(e)}")
            raise

    def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Disease_drug_mappings]:
        try:
            if not hasattr(Disease_drug_mappings, field_name):
                raise ValueError(f"Field {field_name} does not exist on Disease_drug_mappings")
            result = self.db.execute(
                select(Disease_drug_mappings)
                .where(getattr(Disease_drug_mappings, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Disease_drug_mappings.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching disease_drug_mappingss by {field_name}: {str(e)}")
            raise
