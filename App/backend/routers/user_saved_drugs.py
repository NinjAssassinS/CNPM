from datetime import datetime
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models.user_saved_drugs import UserSavedDrug
from models.drugs import Drugs
from schemas.auth import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/user", tags=["user-saved-drugs"])


class SavedDrugResponse(BaseModel):
    id: int
    drug_name: str
    saved_at: Optional[str] = None
    drug_id: Optional[int] = None
    code: Optional[str] = None
    group_name: Optional[str] = None
    manufacturer: Optional[str] = None
    rating: Optional[float] = None
    price: Optional[str] = None
    component: Optional[str] = None
    usage_info: Optional[str] = None
    dosage: Optional[str] = None
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None
    data_source: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class SavedDrugListResponse(BaseModel):
    items: List[SavedDrugResponse]
    total: int


class SaveStatusResponse(BaseModel):
    saved: bool
    message: str


@router.get("/saved-drugs", response_model=SavedDrugListResponse)
def list_saved_drugs(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_details: bool = True,
):
    query = (
        select(UserSavedDrug)
        .where(UserSavedDrug.user_id == current_user.id)
        .order_by(UserSavedDrug.saved_at.desc())
    )
    result = db.execute(query)
    items = result.scalars().all()

    # Fetch drug details from the drugs table (match by name or by numeric ID)
    drug_names = [item.drug_name for item in items]
    drug_details = {}
    drug_id_details = {}
    if drug_names:
        drugs_result = db.execute(
            select(Drugs).where(Drugs.name.in_(drug_names))
        )
        for drug in drugs_result.scalars().all():
            drug_details[drug.name] = drug

        # Also try matching by numeric ID for backward compatibility
        numeric_ids = [n for n in drug_names if n.isdigit()]
        if numeric_ids:
            drugs_by_id = db.execute(
                select(Drugs).where(Drugs.id.in_([int(n) for n in numeric_ids]))
            )
            for drug in drugs_by_id.scalars().all():
                drug_id_details[str(drug.id)] = drug

    def to_response(item: UserSavedDrug) -> SavedDrugResponse:
        drug = drug_details.get(item.drug_name) or drug_id_details.get(item.drug_name)
        if drug:
            return SavedDrugResponse(
                id=item.id,
                drug_name=item.drug_name,
                saved_at=item.saved_at.isoformat() if item.saved_at else None,
                drug_id=drug.id,
                code=drug.code,
                group_name=drug.group_name,
                manufacturer=drug.manufacturer,
                rating=drug.rating,
                price=drug.price,
                component=drug.component,
                usage_info=drug.usage_info,
                dosage=drug.dosage,
                side_effects=drug.side_effects,
                contraindications=drug.contraindications,
                data_source="local",
                status=drug.status,
            )
        return SavedDrugResponse(
            id=item.id,
            drug_name=item.drug_name,
            saved_at=item.saved_at.isoformat() if item.saved_at else None,
            data_source="openfda",
        )

    return SavedDrugListResponse(
        items=[to_response(item) for item in items],
        total=len(items),
    )


def _resolve_drug_name(drug_name: str, db: Session) -> str:
    """If drug_name is a numeric ID, look up the actual drug name from the drugs table."""
    if drug_name.isdigit():
        drug = db.execute(
            select(Drugs).where(Drugs.id == int(drug_name))
        ).scalar_one_or_none()
        if drug:
            return drug.name
    return drug_name


@router.post("/saved-drugs/{drug_name:path}", response_model=SaveStatusResponse)
def save_drug(
    drug_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actual_name = _resolve_drug_name(drug_name, db)

    existing = db.execute(
        select(UserSavedDrug).where(
            UserSavedDrug.user_id == current_user.id,
            UserSavedDrug.drug_name == actual_name,
        )
    ).scalar_one_or_none()

    if existing:
        return SaveStatusResponse(saved=True, message="Drug already saved")

    saved = UserSavedDrug(
        user_id=current_user.id,
        drug_name=actual_name,
    )
    db.add(saved)
    db.commit()

    return SaveStatusResponse(saved=True, message="Drug saved successfully")


@router.delete("/saved-drugs/{drug_name:path}", response_model=SaveStatusResponse)
def unsave_drug(
    drug_name: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actual_name = _resolve_drug_name(drug_name, db)

    result = db.execute(
        delete(UserSavedDrug).where(
            UserSavedDrug.user_id == current_user.id,
            UserSavedDrug.drug_name == actual_name,
        )
    )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Saved drug not found")

    db.commit()

    return SaveStatusResponse(saved=False, message="Drug unsaved successfully")
