"""Switch from drug_id to drug_name for OpenFDA integration

Revision ID: c3d4e5f6a7b8
Revises: b2f974d53e17
Create Date: 2026-06-22 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2f974d53e17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # disease_drug_mappings: add drug_name, remove drug_id
    op.add_column("disease_drug_mappings", sa.Column("drug_name", sa.Unicode(500), nullable=True))
    op.drop_column("disease_drug_mappings", "drug_id")

    # user_saved_drugs: remove FK to drugs.id, make drug_name primary
    op.drop_constraint("uq_user_drug", "user_saved_drugs", type_="unique")
    op.drop_column("user_saved_drugs", "drug_id")
    op.alter_column("user_saved_drugs", "drug_name", type_=sa.String(500), nullable=False)
    op.create_unique_constraint("uq_user_drug_name", "user_saved_drugs", ["user_id", "drug_name"])


def downgrade() -> None:
    # Reverse disease_drug_mappings
    op.add_column("disease_drug_mappings", sa.Column("drug_id", sa.Integer(), nullable=False))
    op.drop_column("disease_drug_mappings", "drug_name")

    # Reverse user_saved_drugs
    op.drop_constraint("uq_user_drug_name", "user_saved_drugs", type_="unique")
    op.alter_column("user_saved_drugs", "drug_name", type_=sa.String(200), nullable=True)
    op.add_column("user_saved_drugs", sa.Column("drug_id", sa.Integer(), sa.ForeignKey("drugs.id"), nullable=False))
    op.create_unique_constraint("uq_user_drug", "user_saved_drugs", ["user_id", "drug_id"])
