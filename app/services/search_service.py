import difflib
from datetime import datetime, timedelta

class SearchError(Exception):
    pass

class SearchService:
    def __init__(self, repository):
        self.repository = repository

    def resolve_country(self, text: str) -> str:
        countries = self.repository.countries()
        for name in countries:
            if name.lower() == text.strip().lower():
                return name
        similar = difflib.get_close_matches(text, countries, n=3, cutoff=0.6)
        hint = f" Можливо, ви мали на увазі: {', '.join(similar)}?" if similar else ""
        raise SearchError(f"Країну '{text}' не знайдено.{hint}")

    def search(self, country_text: str, date_text: str, city: str | None = None):
        try:
            start = datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            raise SearchError("Дату треба вводити у форматі РРРР-ММ-ДД, наприклад 2025-03-15")

        country = self.resolve_country(country_text)
        records = self.repository.find(country, start, start + timedelta(days=1), city)

        if not records:
            first, last = self.repository.date_range(country)
            where = f"{country}, {city}" if city else country
            raise SearchError(
                f"Для {where} за {date_text} даних немає. "
                f"По країні {country} дані є з {first:%Y-%m-%d} по {last:%Y-%m-%d}."
            )
        return country, records