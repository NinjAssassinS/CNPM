from core.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Unicode


class Disease_drug_mappings(Base):
    __tablename__ = "disease_drug_mappings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    disease_id = Column(Integer, nullable=False)
    drug_name = Column(Unicode(500), nullable=False)
    priority = Column(Integer, nullable=False)
    match_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
