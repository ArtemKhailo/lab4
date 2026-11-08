from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload
from app.models import AirQuality, Weather

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

