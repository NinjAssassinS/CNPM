import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from core.database import Base, db_manager
from models.disease_drug_mappings import Disease_drug_mappings
from models.diseases import Diseases
from models.drugs import Drugs
from models.prediction_histories import Prediction_histories
from sqlalchemy import MetaData, Table
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError

logger = logging.getLogger(__name__)

MOCK_DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data"

# Map table names to ORM model classes for reliable inserts
MODEL_MAP: Dict[str, Type[Base]] = {
    "diseases": Diseases,
    "drugs": Drugs,
    "disease_drug_mappings": Disease_drug_mappings,
    "prediction_histories": Prediction_histories,
}


def _parse_json_file(data_file: Path) -> Optional[List[Dict[str, Any]]]:
    """Read and parse a JSON file, returning a list of dict records."""
    try:
        raw_bytes = data_file.read_bytes()
        if raw_bytes[:3] == b'\xef\xbb\xbf':
            raw_bytes = raw_bytes[3:]
        raw_records = json.loads(raw_bytes.decode("utf-8"))
        if isinstance(raw_records, dict):
            return [raw_records]
        if isinstance(raw_records, list):
            return [item for item in raw_records if isinstance(item, dict)]
        logger.warning("Unexpected JSON structure in %s", data_file.name)
        return None
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", data_file.name, exc)
        return None


def _load_via_core(data_file: Path, table_name: str) -> Optional[int]:
    """Attempt to load mock data using Core-level bulk insert."""
    with db_manager.engine.begin() as conn:
        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=conn)
        except NoSuchTableError:
            logger.warning("Table %s does not exist; cannot load via Core", table_name)
            return None
        except SQLAlchemyError as exc:
            logger.error("Failed to reflect table %s: %s", table_name, exc)
            return None

        row_count = conn.scalar(select(func.count()).select_from(table))
        if row_count and row_count > 0:
            logger.info("Table %s already has %d rows; skipping", table_name, row_count)
            return 0

    records = _parse_json_file(data_file)
    if not records:
        return None

    with db_manager.engine.begin() as conn:
        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=conn)
        except Exception:
            return None

        column_map = {column.name: column for column in table.columns}
        prepared = []
        for entry in records:
            filtered = {}
            for key, value in entry.items():
                if key not in column_map:
                    continue
                column = column_map[key]
                filtered[key] = _coerce_value(value, column)
            if filtered:
                prepared.append(filtered)

        if not prepared:
            logger.warning("No valid records for Core insert in %s", data_file.name)
            return None

        try:
            conn.execute(table.insert(), prepared)
            count = len(prepared)
            logger.info("Core insert: %d records into %s", count, table_name)
            return count
        except SQLAlchemyError as exc:
            logger.error("Core insert failed for %s: %s", table_name, exc)
            return None


def _load_via_orm(data_file: Path, table_name: str, model_class: Type[Base]) -> Optional[int]:
    """Load mock data using ORM models to ensure Python-level defaults are applied."""
    records = _parse_json_file(data_file)
    if not records:
        return None

    with db_manager.session_maker() as session:
        try:
            existing = session.query(model_class).first()
            if existing is not None:
                count = session.query(model_class).count()
                logger.info("Table %s already has %d rows (ORM check); skipping", table_name, count)
                return 0
        except Exception as exc:
            logger.warning("ORM count check failed for %s: %s", table_name, exc)
            return None

        # Get column names from the model (exclude id for auto-increment)
        model_columns = [c.name for c in model_class.__table__.columns if c.name != "id"]

        instances = []
        for entry in records:
            filtered = {k: v for k, v in entry.items() if k in model_columns}
            if filtered:
                instances.append(model_class(**filtered))

        if not instances:
            logger.warning("No valid ORM instances for %s", data_file.name)
            return None

        try:
            for inst in instances:
                session.add(inst)
            session.commit()
            count = len(instances)
            logger.info("ORM insert: %d records into %s", count, table_name)
            return count
        except Exception as exc:
            session.rollback()
            logger.error("ORM insert failed for %s: %s", table_name, exc)
            return None


def initialize_mock_data():
    """Populate tables with mock JSON data when they are empty.

    Uses ORM-based inserts (which preserve Python-level defaults) as the primary
    method, falling back to Core-level bulk inserts for tables without a model.
    """
    if "MGX_IGNORE_INIT_DATA" in os.environ:
        logger.info("Ignore initialize data")
        return
    if not db_manager.engine:
        logger.warning("Database engine is not ready; skipping mock data initialization")
        return

    if not MOCK_DATA_DIR.exists():
        logger.info("mock_data directory not found, skipping mock initialization")
        return

    data_files = sorted(MOCK_DATA_DIR.glob("*.json"))
    if not data_files:
        logger.info("No mock JSON files detected; skipping mock initialization")
        return

    for data_file in data_files:
        table_name = data_file.stem
        logger.info("Processing mock data file %s for table %s", data_file.name, table_name)
        try:
            if table_name in MODEL_MAP:
                result = _load_via_orm(data_file, table_name, MODEL_MAP[table_name])
                if result is None:
                    logger.warning("ORM load failed for %s, trying Core fallback", table_name)
                    _load_via_core(data_file, table_name)
            else:
                _load_via_core(data_file, table_name)
        except Exception as exc:
            logger.error("Unexpected error loading %s: %s", data_file.name, exc)


def _coerce_value(value: Any, column) -> Any:
    """Coerce nested structures to JSON strings when the column is not JSON."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        visit_name = getattr(column.type, "__visit_name__", "").lower()
        if "json" in visit_name:
            return value
        return json.dumps(value, ensure_ascii=False)
    return value