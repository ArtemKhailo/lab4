"""move air quality to separate table
Revision ID: 0002
Revises: 0001
Create Date: 2026-11-08 22:49:58.134220
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
COLUMNS = {
    "air_quality_carbon_monoxide": "carbon_monoxide",
    "air_quality_ozone": "ozone",
    "air_quality_nitrogen_dioxide": "nitrogen_dioxide",
    "air_quality_sulphur_dioxide": "sulphur_dioxide",
    "air_quality_pm2_5": "pm2_5",
    "air_quality_pm10": "pm10",
    "air_quality_us_epa_index": "us_epa_index",
    "air_quality_gb_defra_index": "gb_defra_index",
}
INTEGER_COLUMNS = {"air_quality_us_epa_index", "air_quality_gb_defra_index"}

def column_type(old_name):
    return sa.Integer() if old_name in INTEGER_COLUMNS else sa.Double()

def upgrade() -> None:
    op.create_table(
        "air_quality",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "weather_id",
            sa.Integer(),
            sa.ForeignKey("weather.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        *[sa.Column(new, column_type(old), nullable=True) for old, new in COLUMNS.items()],
    )

    new_cols = ", ".join(COLUMNS.values())
    old_cols = ", ".join(COLUMNS.keys())
    op.execute(
        f"INSERT INTO air_quality (weather_id, {new_cols}) "
        f"SELECT id, {old_cols} FROM weather"
    )

    for old in COLUMNS:
        op.drop_column("weather", old)


def downgrade() -> None:
    for old in COLUMNS:
        op.add_column("weather", sa.Column(old, column_type(old), nullable=True))

    if op.get_bind().dialect.name == "mysql":
        sets = ", ".join(f"w.{old} = a.{new}" for old, new in COLUMNS.items())
        op.execute(f"UPDATE weather w JOIN air_quality a ON a.weather_id = w.id SET {sets}")
    else:
        sets = ", ".join(f"{old} = a.{new}" for old, new in COLUMNS.items())
        op.execute(f"UPDATE weather SET {sets} FROM air_quality a WHERE a.weather_id = weather.id")

    op.drop_table("air_quality")
