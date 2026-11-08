from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import selectinload
from app.models import AirQuality, Weather
from datetime import datetime

class WeatherRepository:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def count(self) -> int:
        with self._session_factory() as session:
            return session.scalar(select(func.count()).select_from(Weather))

    def delete_all(self) -> None:
        with self._session_factory() as session:
            session.execute(delete(AirQuality))
            session.execute(delete(Weather))
            session.commit()

    def bulk_insert(self, rows: list[dict]) -> int:
        with self._session_factory() as session:
            for row in rows:
                air = row.pop("air_quality")
                session.add(Weather(**row, air_quality=AirQuality(**air)))
            session.commit()
        return len(rows)

    def sample(self, limit: int = 10) -> list[Weather]:
        with self._session_factory() as session:
            query = (
                select(Weather)
                .options(selectinload(Weather.air_quality))
                .order_by(Weather.id)
                .limit(limit)
            )
            return list(session.scalars(query))
    
    def summary(self) -> dict:
        with self._session_factory() as session:
            total, countries, first, last = session.execute(
                select(
                    func.count(Weather.id),
                    func.count(func.distinct(Weather.country)),
                    func.min(Weather.last_updated),
                    func.max(Weather.last_updated),
                )
            ).one()
        return {"total": total, "countries": countries, "first": first, "last": last}

    def air_quality_batches(self, batch_size: int):
        last_id = 0
        while True:
            with self._session_factory() as session:
                rows = session.execute(
                    select(AirQuality.id, AirQuality.pm2_5, AirQuality.us_epa_index)
                    .where(AirQuality.id > last_id)
                    .order_by(AirQuality.id)
                    .limit(batch_size)
                ).all()
            if not rows:
                break
            yield rows
            last_id = rows[-1].id

    def update_go_outside(self, values: list[dict]) -> None:
        with self._session_factory() as session:
            session.execute(update(AirQuality), values)
            session.commit()

    def countries(self) -> list[str]:
        with self._session_factory() as session:
            return list(session.scalars(
                select(Weather.country).distinct().order_by(Weather.country)
            ))

    def find(self, country: str, start: datetime, end: datetime, city: str | None = None) -> list[Weather]:
        with self._session_factory() as session:
            query = (
                select(Weather)
                .options(selectinload(Weather.air_quality))
                .where(Weather.country == country)
                .where(Weather.last_updated >= start)
                .where(Weather.last_updated < end)
                .order_by(Weather.last_updated)
            )
            if city:
                query = query.where(func.lower(Weather.location_name) == city.lower())
            return list(session.scalars(query))

    def date_range(self, country: str):
        with self._session_factory() as session:
            return session.execute(
                select(func.min(Weather.last_updated), func.max(Weather.last_updated))
                .where(Weather.country == country)
            ).one()

