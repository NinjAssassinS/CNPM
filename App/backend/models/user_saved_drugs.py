from core.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint


class UserSavedDrug(Base):
    __tablename__ = "user_saved_drugs"
    __table_args__ = (
        UniqueConstraint("user_id", "drug_name", name="uq_user_drug_name"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    drug_name = Column(String(500), nullable=False)
    saved_at = Column(DateTime, default=datetime.now)
