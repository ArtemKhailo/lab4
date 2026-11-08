from sqlalchemy import Double, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weather_id: Mapped[int] = mapped_column(
        ForeignKey("weather.id", ondelete="CASCADE"), unique=True, nullable=False)

    carbon_monoxide: Mapped[float | None] = mapped_column(Double)
    ozone: Mapped[float | None] = mapped_column(Double)
    nitrogen_dioxide: Mapped[float | None] = mapped_column(Double)
    sulphur_dioxide: Mapped[float | None] = mapped_column(Double)
    pm2_5: Mapped[float | None] = mapped_column(Double)
    pm10: Mapped[float | None] = mapped_column(Double)
    us_epa_index: Mapped[int | None] = mapped_column(Integer)
    gb_defra_index: Mapped[int | None] = mapped_column(Integer)

    weather: Mapped["Weather"] = relationship(back_populates="air_quality")