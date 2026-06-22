#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script lấy dữ liệu thuốc từ OpenFDA API và dịch sang tiếng Việt.

Cách dùng:
  python scripts/fetch_openfda.py                     # Chạy mặc định (lấy 50 thuốc)
  python scripts/fetch_openfda.py --limit 200          # Lấy 200 thuốc
  python scripts/fetch_openfda.py --translate          # Dịch dữ liệu sang tiếng Việt
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MOCK_DIR = Path(__file__).resolve().parent.parent / "mock_data"
os.makedirs(MOCK_DIR, exist_ok=True)

OPENFDA_BASE = "https://api.fda.gov/drug"
API_KEY = "cYzhzoHiQdDiwxC3w3smJ5Fp5rlpKudgLVvgrkQ9"

# Vietnamese medical terminology dictionary for translation
VIETNAMESE_MEDICAL_DICT = {
    # Drug categories
    "ANALGESICS": "Giảm đau",
    "ANTI-ALLERGIC": "Chống dị ứng",
    "ANTI-INFECTIVE": "Kháng nhiễm khuẩn",
    "ANTIBACTERIAL": "Kháng sinh",
    "ANTIBIOTIC": "Kháng sinh",
    "ANTICOAGULANT": "Chống đông máu",
    "ANTICONVULSANT": "Chống động kinh",
    "ANTIDEPRESSANT": "Chống trầm cảm",
    "ANTIDIABETIC": "Tiểu đường",
    "ANTIDIARRHEAL": "Chống tiêu chảy",
    "ANTIEMETIC": "Chống nôn",
    "ANTIFUNGAL": "Kháng nấm",
    "ANTIHISTAMINE": "Kháng histamin",
    "ANTHYPERTENSIVE": "Hạ huyết áp",
    "ANTI-INFLAMMATORY": "Kháng viêm",
    "ANTINEOPLASTIC": "Chống ung thư",
    "ANTIPYRETIC": "Hạ sốt",
    "ANTIVIRAL": "Kháng virus",
    "ANXIOLYTIC": "Giải lo âu",
    "BRONCHODILATOR": "Giãn phế quản",
    "CARDIOVASCULAR": "Tim mạch",
    "CENTRAL NERVOUS SYSTEM": "Thần kinh trung ương",
    "CONTRACEPTIVE": "Tránh thai",
    "CORTICOSTEROID": "Corticoid",
    "COUGH SUPPRESSANT": "Giảm ho",
    "DECONGESTANT": "Thông mũi",
    "DERMATOLOGICAL": "Da liễu",
    "DIURETIC": "Lợi tiểu",
    "ELECTROLYTE": "Điện giải",
    "EXPECTORANT": "Long đờm",
    "GASTROINTESTINAL": "Tiêu hóa",
    "HEMATINIC": "Bổ máu",
    "HEMOSTATIC": "Cầm máu",
    "HORMONAL": "Nội tiết tố",
    "HYPOGLYCEMIC": "Hạ đường huyết",
    "HYPNOTIC": "An thần",
    "IMMUNOSUPPRESSANT": "Ức chế miễn dịch",
    "LAXATIVE": "Nhuận tràng",
    "LIPID LOWERING": "Hạ mỡ máu",
    "MUSCLE RELAXANT": "Giãn cơ",
    "NARCOTIC": "Gây nghiện",
    "NSAID": "Kháng viêm không steroid",
    "OPHTHALMIC": "Mắt",
    "OPIOID": "Giảm đau gây nghiện",
    "OTIC": "Tai",
    "PSYCHOTHERAPEUTIC": "Tâm thần",
    "RESPIRATORY": "Hô hấp",
    "SEDATIVE": "An thần",
    "THYROID": "Tuyến giáp",
    "VACCINE": "Vắc xin",
    "VASODILATOR": "Giãn mạch",
    "VITAMIN": "Vitamin",

    # Common medical terms
    "TABLET": "Viên nén",
    "CAPSULE": "Viên nang",
    "INJECTION": "Thuốc tiêm",
    "SOLUTION": "Dung dịch",
    "SUSPENSION": "Hỗn dịch",
    "CREAM": "Kem bôi",
    "OINTMENT": "Thuốc mỡ",
    "EYE DROPS": "Thuốc nhỏ mắt",
    "NASAL SPRAY": "Xịt mũi",
    "INHALATION": "Thuốc hít",
    "PATCH": "Miếng dán",
    "SYRUP": "Si rô",
    "ORAL": "Đường uống",
    "TOPICAL": "Bôi ngoài da",
    "INTRAVENOUS": "Đường tĩnh mạch",
    "INTRAMUSCULAR": "Đường tiêm bắp",
    "SUBCUTANEOUS": "Dưới da",

    # Side effect / warning terms
    "NAUSEA": "Buồn nôn",
    "VOMITING": "Nôn",
    "HEADACHE": "Đau đầu",
    "DIZZINESS": "Chóng mặt",
    "DIARRHEA": "Tiêu chảy",
    "CONSTIPATION": "Táo bón",
    "RASH": "Phát ban",
    "FATIGUE": "Mệt mỏi",
    "DROWSINESS": "Buồn ngủ",
    "INSOMNIA": "Mất ngủ",
    "HYPOTENSION": "Hạ huyết áp",
    "HYPERTENSION": "Tăng huyết áp",
    "EDEMA": "Phù",
    "PRURITUS": "Ngứa",
    "FEVER": "Sốt",
    "COUGH": "Ho",
    "DYSPNEA": "Khó thở",
    "ANAPHYLAXIS": "Sốc phản vệ",
    "HYPERGLYCEMIA": "Tăng đường huyết",
    "HYPOGLYCEMIA": "Hạ đường huyết",
    "THROMBOCYTOPENIA": "Giảm tiểu cầu",
    "LEUKOPENIA": "Giảm bạch cầu",
    "HEPATOTOXICITY": "Độc gan",
    "NEPHROTOXICITY": "Độc thận",
    "STEVENS-JOHNSON SYNDROME": "Hội chứng Stevens-Johnson",
}

COMMON_DRUG_SEARCHES = [
    "Aspirin", "Ibuprofen", "Acetaminophen", "Amoxicillin", "Metformin",
    "Atorvastatin", "Lisinopril", "Omeprazole", "Losartan", "Amlodipine",
    "Metoprolol", "Simvastatin", "Gabapentin", "Sertraline", "Fluoxetine",
    "Salbutamol", "Prednisone", "Warfarin", "Clopidogrel", "Furosemide",
    "Levothyroxine", "Pantoprazole", "Ciprofloxacin", "Azithromycin", "Doxycycline",
    "Naproxen", "Tramadol", "Morphine", "Insulin", "Nitroglycerin",
    "Digoxin", "Spironolactone", "Carvedilol", "Allopurinol", "Colchicine",
    "Alendronate", "Raloxifene", "Donepezil", "Pregabalin", "Meloxicam",
    "Celecoxib", "Methotrexate", "Hydroxychloroquine", "Sulfasalazine", "Leflunomide",
    "Montelukast", "Budesonide", "Fluticasone", "Tiotropium", "Ipratropium",
]

# Group mapping to standard Vietnamese groups
GROUP_MAPPING = {
    "pain": "Giảm đau - Hạ sốt",
    "fever": "Giảm đau - Hạ sốt",
    "analgesic": "Giảm đau - Hạ sốt",
    "anti-inflammatory": "Giảm đau - Hạ sốt",
    "antibiotic": "Kháng sinh",
    "antibacterial": "Kháng sinh",
    "antiviral": "Kháng virus",
    "cardiovascular": "Tim mạch",
    "blood pressure": "Tim mạch",
    "hypertension": "Tim mạch",
    "cholesterol": "Tim mạch",
    "respiratory": "Hô hấp",
    "asthma": "Hô hấp",
    "allergy": "Hô hấp",
    "antihistamine": "Hô hấp",
    "digestive": "Tiêu hóa",
    "gastrointestinal": "Tiêu hóa",
    "stomach": "Tiêu hóa",
    "diabetes": "Nội tiết",
    "endocrine": "Nội tiết",
    "thyroid": "Nội tiết",
    "neurological": "Thần kinh",
    "nerve": "Thần kinh",
    "antidepressant": "Thần kinh",
    "anxiety": "Thần kinh",
    "psychiatric": "Tâm thần",
    "dermatology": "Da liễu",
    "skin": "Da liễu",
    "antifungal": "Da liễu",
    "vitamin": "Vitamin - Bổ sung",
    "mineral": "Vitamin - Bổ sung",
    "supplement": "Vitamin - Bổ sung",
    "musculoskeletal": "Cơ xương khớp",
    "joint": "Cơ xương khớp",
    "osteoporosis": "Nội tiết",
    "eye": "Mắt",
    "ophthalmic": "Mắt",
    "urinary": "Tiết niệu",
    "kidney": "Tiết niệu",
    "ear": "Tai - Mũi - Họng",
    "nose": "Tai - Mũi - Họng",
    "throat": "Tai - Mũi - Họng",
    "infection": "Truyền nhiễm",
    "vaccine": "Truyền nhiễm",
}

# Vietnamese manufacturers mapping
MANUFACTURER_MAP = {
    "PFIZER": "Pfizer",
    "NOVARTIS": "Novartis",
    "ROCHE": "Roche",
    "SANOFI": "Sanofi",
    "GSK": "GSK",
    "BAYER": "Bayer",
    "MERCK": "Merck",
    "ASTRAZENECA": "AstraZeneca",
    "ABBOTT": "Abbott",
    "JOHNSON": "Johnson & Johnson",
    "BRISTOL": "Bristol-Myers Squibb",
    "BOEHRINGER": "Boehringer Ingelheim",
    "SANDOZ": "Sandoz",
    "MYLAN": "Mylan",
    "TEVA": "Teva",
    "SERVIER": "Servier",
    "TAKEDA": "Takeda",
    "UCB": "UCB",
    "ELI LILLY": "Eli Lilly",
    "NOVO NORDISK": "Novo Nordisk",
    "ALCON": "Alcon",
    "ZAMBON": "Zambon",
    "JANSSEN": "Janssen",
}


def fetch_openfda(endpoint: str, search: str = "", limit: int = 10, skip: int = 0) -> dict:
    """Fetch data from OpenFDA API."""
    import urllib.request
    import urllib.parse

    url = f"{OPENFDA_BASE}/{endpoint}.json"
    params = {"api_key": API_KEY, "limit": limit, "skip": skip}
    if search:
        params["search"] = search
    url += "?" + urllib.parse.urlencode(params)

    logger.info(f"Fetching: {url[:120]}...")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.error(f"Error fetching: {e}")
        return {"error": str(e)}


def extract_drug_from_label(label: dict) -> dict:
    """Extract drug info from a FDA label result."""
    openfda = label.get("openfda", {})
    brand_names = openfda.get("brand_name", [])
    generic_names = openfda.get("generic_name", [])
    manufacturer = openfda.get("manufacturer_name", [])
    product_type = openfda.get("product_type", [])
    route = openfda.get("route", [])
    substance = openfda.get("substance_name", [])
    pharm_class = openfda.get("pharm_class_epc", []) or openfda.get("pharm_class_moa", [])

    indications = label.get("indications_and_usage", [])
    warnings = label.get("warnings", [])
    adverse = label.get("adverse_reactions", [])
    dosage = label.get("dosage_and_administration", [])
    contraindications = label.get("contraindications", [])

    return {
        "brand_name": brand_names[0] if brand_names else "Unknown",
        "generic_name": generic_names[0] if generic_names else "",
        "manufacturer_name": manufacturer[0] if manufacturer else "Unknown",
        "product_type": product_type[0] if product_type else "",
        "route": route,
        "substance_name": substance,
        "pharm_class": pharm_class,
        "indications": indications,
        "warnings": warnings,
        "adverse_reactions": adverse,
        "dosage": dosage,
        "contraindications": contraindications,
    }


def classify_group(indications: list, pharm_class: list, substance: list) -> str:
    """Classify drug into Vietnamese group name based on its properties."""
    text = " ".join(indications + pharm_class + substance).lower()
    for keyword, group in GROUP_MAPPING.items():
        if keyword.lower() in text:
            return group
    return "Khác"


def translate_text(text: str) -> str:
    """Translate common English medical terms to Vietnamese."""
    if not text:
        return ""
    # Simple dictionary-based translation
    result = text
    for eng, vie in sorted(VIETNAMESE_MEDICAL_DICT.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(eng), re.IGNORECASE)
        result = pattern.sub(vie, result)
    return result


def truncate(text: str, max_len: int = 200) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len]


def extract_side_effects(adverse: list) -> str:
    """Extract and translate side effects."""
    if not adverse:
        return ""
    text = "; ".join(adverse)
    text = re.sub(r'<[^>]+>', '', text)
    text = translate_text(text)
    return truncate(text, 500)


def extract_usage(indications: list) -> str:
    if not indications:
        return ""
    text = "; ".join(indications)
    text = re.sub(r'<[^>]+>', '', text)
    text = translate_text(text)
    return truncate(text, 500)


def extract_dosage(dosage_list: list) -> str:
    if not dosage_list:
        return ""
    text = "; ".join(dosage_list[:3])
    text = re.sub(r'<[^>]+>', '', text)
    return truncate(text, 500)


def extract_contraindications(contra: list) -> str:
    if not contra:
        return ""
    text = "; ".join(contra)
    text = re.sub(r'<[^>]+>', '', text)
    text = translate_text(text)
    return truncate(text, 500)


def extract_component(substance: list) -> str:
    return ", ".join(substance) if substance else ""


def to_drug_json(index: int, info: dict) -> dict:
    """Convert FDA data to our Drug model format."""
    group = classify_group(info["indications"], info["pharm_class"], info["substance_name"])
    brand = info["brand_name"]
    generic = info.get("generic_name", "")
    name = f"{brand} ({generic})" if generic and generic.lower() != brand.lower() else brand

    mfr = info["manufacturer_name"].upper()
    manufacturer = "Unknown"
    for key, val in MANUFACTURER_MAP.items():
        if key in mfr:
            manufacturer = val
            break
    if manufacturer == "Unknown":
        manufacturer = info["manufacturer_name"].title()[:50]

    return {
        "code": f"FDA{index:04d}",
        "name": name[:200],
        "group_name": group,
        "manufacturer": manufacturer,
        "status": "active",
        "rating": round(4.0 + (hash(name) % 10) / 10, 1),
        "price": f"{50 + (hash(name) % 150)}.000đ",
        "component": extract_component(info["substance_name"])[:500],
        "usage_info": extract_usage(info["indications"])[:1000],
        "dosage": extract_dosage(info["dosage"])[:500],
        "side_effects": extract_side_effects(info["adverse_reactions"])[:1000],
        "contraindications": extract_contraindications(info["contraindications"])[:1000],
    }


def fetch_drugs(limit: int = 50) -> list:
    """Fetch drugs from OpenFDA label endpoint using targeted searches."""
    all_drugs = []
    seen_names = set()
    drug_index = 0

    # First, try to get commonly known drugs by searching for them
    searches = COMMON_DRUG_SEARCHES + ["antibiotic", "pain", "heart", "diabetes"]
    for query in searches:
        if len(all_drugs) >= limit:
            break
        logger.info(f"Searching for: {query}")
        data = fetch_openfda("label", search=f"openfda.brand_name:{query}", limit=10, skip=0)
        if data.get("error") or "results" not in data:
            continue
        results = data["results"]
        for label in results:
            if len(all_drugs) >= limit:
                break
            info = extract_drug_from_label(label)
            name_lower = info["brand_name"].lower()
            # Skip homeopathic and unknown
            if not info["brand_name"] or info["brand_name"] == "Unknown":
                continue
            if "homeopathic" in name_lower or "unknown" in name_lower:
                continue
            if info["brand_name"] in seen_names:
                continue
            seen_names.add(info["brand_name"])
            drug_index += 1
            drug = to_drug_json(drug_index, info)
            all_drugs.append(drug)
            logger.info(f"  [{drug_index}] {drug['name']} ({drug['group_name']})")
        time.sleep(0.3)

    # Fill remaining with general fetch
    if len(all_drugs) < limit:
        skip = 0
        while len(all_drugs) < limit:
            batch = min(50, limit - len(all_drugs))
            logger.info(f"Fetching general batch at skip={skip}...")
            data = fetch_openfda("label", search="", limit=batch, skip=skip)
            if data.get("error") or "results" not in data:
                break
            results = data["results"]
            if not results:
                break
            for label in results:
                if len(all_drugs) >= limit:
                    break
                info = extract_drug_from_label(label)
                if info["brand_name"] == "Unknown" or info["brand_name"] in seen_names:
                    continue
                seen_names.add(info["brand_name"])
                drug_index += 1
                drug = to_drug_json(drug_index, info)
                all_drugs.append(drug)
                logger.info(f"  [{drug_index}] {drug['name']} ({drug['group_name']})")
            skip += 50
            time.sleep(0.5)

    return all_drugs


def save_json(data: list, filename: str):
    filepath = MOCK_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(data)} records to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Fetch drug data from OpenFDA and translate to Vietnamese")
    parser.add_argument("--limit", type=int, default=50, help="Number of drugs to fetch")
    args = parser.parse_args()

    logger.info(f"Fetching {args.limit} drugs from OpenFDA...")
    drugs = fetch_drugs(args.limit)

    if drugs:
        save_json(drugs, "drugs_openfda.json")
        logger.info(f"Total: {len(drugs)} drugs fetched and translated to Vietnamese")
    else:
        logger.warning("No drugs fetched!")
        sys.exit(1)


if __name__ == "__main__":
    main()
