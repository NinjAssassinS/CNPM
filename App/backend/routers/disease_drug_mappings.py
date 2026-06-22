import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.disease_drug_mappings import Disease_drug_mappingsService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/disease_drug_mappings", tags=["disease_drug_mappings"])


# ---------- Pydantic Schemas ----------
class Disease_drug_mappingsData(BaseModel):
    """Entity data schema (for create/update)"""
    disease_id: int
    drug_name: str
    priority: int
    match_score: int = None


class Disease_drug_mappingsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    disease_id: Optional[int] = None
    drug_name: Optional[str] = None
    priority: Optional[int] = None
    match_score: Optional[int] = None


class Disease_drug_mappingsResponse(BaseModel):
    """Entity response schema"""
    id: int
    disease_id: int
    drug_name: str
    priority: int
    match_score: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Disease_drug_mappingsListResponse(BaseModel):
    """List response schema"""
    items: List[Disease_drug_mappingsResponse]
    total: int
    skip: int
    limit: int


class Disease_drug_mappingsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Disease_drug_mappingsData]


class Disease_drug_mappingsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Disease_drug_mappingsUpdateData


class Disease_drug_mappingsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Disease_drug_mappingsBatchUpdateItem]


class Disease_drug_mappingsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=Disease_drug_mappingsListResponse)
def query_disease_drug_mappingss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    """Query disease_drug_mappingss with filtering, sorting, and pagination"""
    logger.debug(f"Querying disease_drug_mappingss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = Disease_drug_mappingsService(db)
    try:
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        
        result = service.get_list(
            skip=skip, 
            limit=limit,
            query_dict=query_dict,
            sort=sort,
        )
        logger.debug(f"Found {result['total']} disease_drug_mappingss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying disease_drug_mappingss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Disease_drug_mappingsListResponse)
def query_disease_drug_mappingss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    logger.debug(f"Querying disease_drug_mappingss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Disease_drug_mappingsService(db)
    try:
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")

        result = service.get_list(
            skip=skip,
            limit=limit,
            query_dict=query_dict,
            sort=sort
        )
        logger.debug(f"Found {result['total']} disease_drug_mappingss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying disease_drug_mappingss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Disease_drug_mappingsResponse)
def get_disease_drug_mappings(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    """Get a single disease_drug_mappings by ID"""
    logger.debug(f"Fetching disease_drug_mappings with id: {id}, fields={fields}")
    
    service = Disease_drug_mappingsService(db)
    try:
        result = service.get_by_id(id)
        if not result:
            logger.warning(f"Disease_drug_mappings with id {id} not found")
            raise HTTPException(status_code=404, detail="Disease_drug_mappings not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching disease_drug_mappings {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Disease_drug_mappingsResponse, status_code=201)
def create_disease_drug_mappings(
    data: Disease_drug_mappingsData,
    db: Session = Depends(get_db),
):
    """Create a new disease_drug_mappings"""
    logger.debug(f"Creating new disease_drug_mappings with data: {data}")
    
    service = Disease_drug_mappingsService(db)
    try:
        result = service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create disease_drug_mappings")
        
        logger.info(f"Disease_drug_mappings created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating disease_drug_mappings: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating disease_drug_mappings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Disease_drug_mappingsResponse], status_code=201)
def create_disease_drug_mappingss_batch(
    request: Disease_drug_mappingsBatchCreateRequest,
    db: Session = Depends(get_db),
):
    """Create multiple disease_drug_mappingss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} disease_drug_mappingss")
    
    service = Disease_drug_mappingsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} disease_drug_mappingss successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Disease_drug_mappingsResponse])
def update_disease_drug_mappingss_batch(
    request: Disease_drug_mappingsBatchUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update multiple disease_drug_mappingss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} disease_drug_mappingss")
    
    service = Disease_drug_mappingsService(db)
    results = []
    
    try:
        for item in request.items:
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} disease_drug_mappingss successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Disease_drug_mappingsResponse)
def update_disease_drug_mappings(
    id: int,
    data: Disease_drug_mappingsUpdateData,
    db: Session = Depends(get_db),
):
    """Update an existing disease_drug_mappings"""
    logger.debug(f"Updating disease_drug_mappings {id} with data: {data}")

    service = Disease_drug_mappingsService(db)
    try:
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = service.update(id, update_dict)
        if not result:
            logger.warning(f"Disease_drug_mappings with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Disease_drug_mappings not found")
        
        logger.info(f"Disease_drug_mappings {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating disease_drug_mappings {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating disease_drug_mappings {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
def delete_disease_drug_mappingss_batch(
    request: Disease_drug_mappingsBatchDeleteRequest,
    db: Session = Depends(get_db),
):
    """Delete multiple disease_drug_mappingss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} disease_drug_mappingss")
    
    service = Disease_drug_mappingsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} disease_drug_mappingss successfully")
        return {"message": f"Successfully deleted {deleted_count} disease_drug_mappingss", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
def delete_disease_drug_mappings(
    id: int,
    db: Session = Depends(get_db),
):
    """Delete a single disease_drug_mappings by ID"""
    logger.debug(f"Deleting disease_drug_mappings with id: {id}")
    
    service = Disease_drug_mappingsService(db)
    try:
        success = service.delete(id)
        if not success:
            logger.warning(f"Disease_drug_mappings with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Disease_drug_mappings not found")
        
        logger.info(f"Disease_drug_mappings {id} deleted successfully")
        return {"message": "Disease_drug_mappings deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting disease_drug_mappings {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
