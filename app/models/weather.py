from datetime import datetime, time
from sqlalchemy import DateTime, Double, Enum, Index, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.enums import WindDirection

class Weather(Base):
    __tablename__="weather"
    __table_args__=(Index("ix_weather_country_last_updated", "country", "last_updated"),)

    id: Mapped[int]=mapped_column(Integer, primary_key=True, autoincrement=True)

    country: Mapped[str]=mapped_column(String(100), nullable=False)          
    last_updated: Mapped[datetime]=mapped_column(DateTime, nullable=False)   
    wind_degree: Mapped[int | None]=mapped_column(Integer)                   
    wind_kph: Mapped[float | None]=mapped_column(Double)                     
    wind_direction: Mapped[WindDirection | None]=mapped_column(              
        Enum(
            WindDirection,
            name="wind_direction_enum",
            values_callable=lambda e: [m.value for m in e],
        )
    )
    sunrise: Mapped[time | None]=mapped_column(Time)                         

    location_name: Mapped[str]= mapped_column(String(100), nullable=False)
    temperature_celsius: Mapped[float | None]= mapped_column(Double)
    condition_text: Mapped[str | None]= mapped_column(String(100))
    air_quality: Mapped["AirQuality | None"] = relationship(back_populates="weather", cascade="all, delete-orphan")

