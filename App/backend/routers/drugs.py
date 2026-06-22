import json
import logging
from typing import Any, Dict, List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.drugs import DrugsService
from services.openfda import OpenFDAService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/drugs", tags=["drugs"])


@router.get("/search")
async def search_drugs_fast(
    query: str = Query("", description="Search query for drug name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search drugs - local DB first, then OpenFDA fallback."""
    service = DrugsService(db=db)
    try:
        return await service.search_by_name(query, limit=limit, skip=skip)
    except Exception as e:
        logger.error(f"Error searching drugs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/local")
def search_drugs_local(
    query: str = Query("", description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Search drugs in local database only."""
    from services.local_drugs import LocalDrugsService
    service = LocalDrugsService(db)
    try:
        return service.search_by_name(query, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error querying local drugs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ---------- Pydantic Schemas ----------
class DrugsData(BaseModel):
    """Entity data schema (for create/update)"""
    code: str
    name: str
    group_name: str
    manufacturer: str
    status: str
    rating: float = None
    price: str = None
    component: str = None
    usage_info: str = None
    dosage: str = None
    side_effects: str = None
    contraindications: str = None


class DrugsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    code: Optional[str] = None
    name: Optional[str] = None
    group_name: Optional[str] = None
    manufacturer: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    price: Optional[str] = None
    component: Optional[str] = None
    usage_info: Optional[str] = None
    dosage: Optional[str] = None
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None


class DrugsResponse(BaseModel):
    """Entity response schema"""
    id: int
    code: str
    name: str
    group_name: str
    manufacturer: str
    status: str
    rating: Optional[float] = None
    price: Optional[str] = None
    component: Optional[str] = None
    usage_info: Optional[str] = None
    dosage: Optional[str] = None
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DrugsListResponse(BaseModel):
    """List response schema"""
    items: List[DrugsResponse]
    total: int
    skip: int
    limit: int


class DrugsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[DrugsData]


class DrugsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: DrugsUpdateData


class DrugsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[DrugsBatchUpdateItem]


class DrugsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


# ---------- Routes ----------
@router.get("", response_model=DrugsListResponse)
def query_drugss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    """Query drugss with filtering, sorting, and pagination"""
    logger.debug(f"Querying drugss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    service = DrugsService(db)
    try:
        # Parse query JSON if provided
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
        logger.debug(f"Found {result['total']} drugss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying drugss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=DrugsListResponse)
def query_drugss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    # Query drugss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying drugss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = DrugsService(db)
    try:
        # Parse query JSON if provided
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
        logger.debug(f"Found {result['total']} drugss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying drugss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=DrugsResponse)
def get_drugs(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: Session = Depends(get_db),
):
    """Get a single drugs by ID"""
    logger.debug(f"Fetching drugs with id: {id}, fields={fields}")
    
    service = DrugsService(db)
    try:
        result = service.get_by_id(id)
        if not result:
            logger.warning(f"Drugs with id {id} not found")
            raise HTTPException(status_code=404, detail="Drugs not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching drugs {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class DrugsEnrichedResponse(DrugsResponse):
    """Drug response with openFDA enrichment data"""
    fda_data: Optional[Dict[str, Any]] = None


@router.get("/{id}/enriched", response_model=DrugsEnrichedResponse)
async def get_drugs_enriched(
    id: int,
    db: Session = Depends(get_db),
):
    service = DrugsService(db)
    drug = service.get_by_id(id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drugs not found")

    fda_service = OpenFDAService()
    fda_data = await fda_service.enrich_drug_info(
        brand_name=drug.name,
        generic_name=drug.component or "",
    )

    return DrugsEnrichedResponse(
        id=drug.id,
        code=drug.code,
        name=drug.name,
        group_name=drug.group_name,
        manufacturer=drug.manufacturer,
        status=drug.status,
        rating=drug.rating,
        price=drug.price,
        component=drug.component,
        usage_info=drug.usage_info,
        dosage=drug.dosage,
        side_effects=drug.side_effects,
        contraindications=drug.contraindications,
        fda_data=fda_data if fda_data else None,
    )


@router.post("", response_model=DrugsResponse, status_code=201)
def create_drugs(
    data: DrugsData,
    db: Session = Depends(get_db),
):
    """Create a new drugs"""
    logger.debug(f"Creating new drugs with data: {data}")
    
    service = DrugsService(db)
    try:
        result = service.create(data.model_dump())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create drugs")
        
        logger.info(f"Drugs created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating drugs: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating drugs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[DrugsResponse], status_code=201)
def create_drugss_batch(
    request: DrugsBatchCreateRequest,
    db: Session = Depends(get_db),
):
    """Create multiple drugss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} drugss")
    
    service = DrugsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = service.create(item_data.model_dump())
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} drugss successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[DrugsResponse])
def update_drugss_batch(
    request: DrugsBatchUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update multiple drugss in a single request"""
    logger.debug(f"Batch updating {len(request.items)} drugss")
    
    service = DrugsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = service.update(item.id, update_dict)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} drugss successfully")
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=DrugsResponse)
def update_drugs(
    id: int,
    data: DrugsUpdateData,
    db: Session = Depends(get_db),
):
    """Update an existing drugs"""
    logger.debug(f"Updating drugs {id} with data: {data}")

    service = DrugsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = service.update(id, update_dict)
        if not result:
            logger.warning(f"Drugs with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Drugs not found")
        
        logger.info(f"Drugs {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating drugs {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating drugs {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
def delete_drugss_batch(
    request: DrugsBatchDeleteRequest,
    db: Session = Depends(get_db),
):
    """Delete multiple drugss by their IDs"""
    logger.debug(f"Batch deleting {len(request.ids)} drugss")
    
    service = DrugsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = service.delete(item_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} drugss successfully")
        return {"message": f"Successfully deleted {deleted_count} drugss", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
def delete_drugs(
    id: int,
    db: Session = Depends(get_db),
):
    """Delete a single drugs by ID"""
    logger.debug(f"Deleting drugs with id: {id}")
    
    service = DrugsService(db)
    try:
        success = service.delete(id)
        if not success:
            logger.warning(f"Drugs with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Drugs not found")
        
        logger.info(f"Drugs {id} deleted successfully")
        return {"message": "Drugs deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting drugs {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")