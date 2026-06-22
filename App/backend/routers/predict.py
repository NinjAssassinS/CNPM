import json
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.diseases import DiseasesService
from services.disease_drug_mappings import Disease_drug_mappingsService
from services.drugs import DrugsService
from services.aihub import AIHubService
from schemas.aihub import GenTxtRequest, ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predict", tags=["predict"])


class PredictRequest(BaseModel):
    symptoms: str
    disease_name: Optional[str] = None


class PredictResponse(BaseModel):
    disease_id: int
    disease_name: str
    accuracy_score: int
    description: str
    risk_level: str
    group_name: str
    icon: str
    symptoms: Optional[str] = None
    suggested_drugs: list = []
    ai_explanation: Optional[str] = None


@router.post("", response_model=PredictResponse)
async def predict_disease(
    data: PredictRequest,
    db: Session = Depends(get_db),
):
    """Predict disease based on symptoms using AI and database matching"""
    logger.info(f"Prediction request: symptoms={data.symptoms}, disease_name={data.disease_name}")

    diseases_service = DiseasesService(db)
    drugs_service = DrugsService(db)
    mappings_service = Disease_drug_mappingsService(db)

    # Get all diseases for matching
    diseases_result = diseases_service.get_list(skip=0, limit=1000)
    diseases = diseases_result.get("items", [])

    if not diseases:
        logger.warning("Diseases table is empty, attempting to reload mock data...")
        try:
            from services.mock_data import initialize_mock_data
            initialize_mock_data()
            diseases_result = diseases_service.get_list(skip=0, limit=1000)
            diseases = diseases_result.get("items", [])
        except Exception as reload_err:
            logger.error(f"Failed to reload mock data: {reload_err}")

    if not diseases:
        raise HTTPException(status_code=404, detail="No diseases found in database")

    # Build disease info for AI prompt
    disease_info = []
    for d in diseases:
        disease_info.append({
            "id": d.id,
            "name": d.name,
            "symptoms": d.symptoms or "",
            "group": d.group_name,
            "risk": d.risk_level,
        })

    # Use AI to match symptoms to disease
    prompt = f"""Bạn là một hệ thống AI y tế. Dựa trên triệu chứng được mô tả, hãy xác định bệnh phù hợp nhất từ danh sách bệnh có sẵn.

Triệu chứng người dùng mô tả: {data.symptoms}
{"Tên bệnh gợi ý: " + data.disease_name if data.disease_name else ""}

Danh sách bệnh có sẵn:
{json.dumps(disease_info, ensure_ascii=False, indent=2)}

Hãy trả về JSON với format:
{{"disease_id": <id của bệnh phù hợp nhất>, "accuracy_score": <điểm phù hợp từ 60-99>, "explanation": "<giải thích ngắn gọn tại sao chọn bệnh này>"}}

CHỈ trả về JSON, không có text khác."""

    matched_disease_id = None
    accuracy_score = 85
    ai_explanation = None

    try:
        ai_service = AIHubService()
        request = GenTxtRequest(
            messages=[
                ChatMessage(role="system", content="You are a medical AI assistant. Return ONLY valid JSON."),
                ChatMessage(role="user", content=prompt),
            ],
            model="deepseek-v4-pro",
        )

        # Close DB transaction before slow AI call
        db.rollback()

        response = await ai_service.gentxt(request)
        raw_content = response.content.strip()

        # Extract JSON
        if raw_content.startswith("```"):
            match = re.search(r"```(?:json)?\n(.*?)```", raw_content, re.DOTALL)
            if match:
                raw_content = match.group(1).strip()

        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start >= 0 and end > start:
            raw_content = raw_content[start:end + 1]

        result = json.loads(raw_content)
        matched_disease_id = result.get("disease_id")
        accuracy_score = min(99, max(60, result.get("accuracy_score", 85)))
        ai_explanation = result.get("explanation", "")

    except Exception as e:
        logger.warning(f"AI prediction failed, using fallback matching: {str(e)}")
        # Fallback: simple keyword matching
        symptoms_lower = data.symptoms.lower()
        best_match = None
        best_score = 0

        for d in diseases:
            score = 0
            disease_symptoms = (d.symptoms or "").lower()
            for symptom in symptoms_lower.split(","):
                symptom = symptom.strip()
                if symptom and symptom in disease_symptoms:
                    score += 1
            if data.disease_name and data.disease_name.lower() in d.name.lower():
                score += 5
            if score > best_score:
                best_score = score
                best_match = d

        if best_match:
            matched_disease_id = best_match.id
            accuracy_score = min(95, 60 + best_score * 8)
        else:
            matched_disease_id = diseases[0].id
            accuracy_score = 65

    # Fetch matched disease details
    matched_disease = diseases_service.get_by_id(matched_disease_id)
    if not matched_disease:
        matched_disease = diseases[0]
        matched_disease_id = matched_disease.id

    # Get suggested drugs via mappings (using drug_name)
    mappings_result = mappings_service.get_list(
        skip=0, limit=10,
        query_dict={"disease_id": matched_disease_id},
        sort="priority",
    )
    mappings = mappings_result.get("items", [])

    suggested_drugs = []
    for mapping in mappings:
        try:
            drug = await drugs_service.get_by_generic_name(mapping.drug_name)
            if drug:
                suggested_drugs.append({
                    "id": drug.get("id", hash(mapping.drug_name)),
                    "name": drug.get("name", mapping.drug_name),
                    "generic_name": drug.get("generic_name", mapping.drug_name),
                    "code": drug.get("code", ""),
                    "group_name": drug.get("group_name", "FDA"),
                    "manufacturer": drug.get("manufacturer", "FDA"),
                    "price": drug.get("price", ""),
                    "rating": drug.get("rating", 0),
                    "usage_info": drug.get("usage_info", ""),
                    "dosage": drug.get("dosage", ""),
                    "match_score": mapping.match_score,
                    "priority": mapping.priority,
                    "data_source": drug.get("data_source", "openfda"),
                })
        except Exception as e:
            logger.warning(f"Failed to fetch drug {mapping.drug_name}: {str(e)}")
            suggested_drugs.append({
                "id": hash(mapping.drug_name),
                "name": mapping.drug_name,
                "generic_name": mapping.drug_name,
                "code": "",
                "group_name": "FDA",
                "manufacturer": "FDA",
                "price": "",
                "rating": 0,
                "usage_info": "",
                "dosage": "",
                "match_score": mapping.match_score,
                "priority": mapping.priority,
                "data_source": "openfda",
            })

    return PredictResponse(
        disease_id=matched_disease.id,
        disease_name=matched_disease.name,
        accuracy_score=accuracy_score,
        description=matched_disease.description,
        risk_level=matched_disease.risk_level,
        group_name=matched_disease.group_name,
        icon=matched_disease.icon or "🏥",
        symptoms=matched_disease.symptoms,
        suggested_drugs=suggested_drugs,
        ai_explanation=ai_explanation,
    )