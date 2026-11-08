import csv
from datetime import datetime, time
from pathlib import Path
from app.models.enums import WindDirection

REQUIRED_COLUMNS = [
    "country", "location_name", "last_updated", "temperature_celsius",
    "condition_text", "wind_kph", "wind_degree", "wind_direction", "sunrise",
    "air_quality_Carbon_Monoxide", "air_quality_Ozone",
    "air_quality_Nitrogen_dioxide", "air_quality_Sulphur_dioxide",
    "air_quality_PM2.5", "air_quality_PM10",
    "air_quality_us-epa-index", "air_quality_gb-defra-index",
]

def to_text(value): 
    value = (value or "").strip()
    return value[:100] if value else None

def to_float(value):
    value=(value or "").strip()
    if value.lower() in ("", "nan", "na", "null"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def to_pollutant(value):
    number= to_float(value)
    return number if number is not None and number >= 0 else None

def to_int(value):
    number= to_float(value)
    return int(number) if number is not None else None

def to_datetime(value):
    try:
        return datetime.strptime((value or "").strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        return None

def to_time(value):
    try:
        return datetime.strptime((value or "").strip().upper(), "%I:%M %p").time()
    except ValueError:
        return None

def to_wind_direction(value):
    try:
        return WindDirection((value or "").strip().upper())
    except ValueError:
        return None

def convert_row(raw: dict) -> dict | None:
    row = {
        "country": to_text(raw["country"]),
        "location_name": to_text(raw["location_name"]),
        "last_updated": to_datetime(raw["last_updated"]),
        "temperature_celsius": to_float(raw["temperature_celsius"]),
        "condition_text": to_text(raw["condition_text"]),
        "wind_kph": to_float(raw["wind_kph"]),
        "wind_degree": to_int(raw["wind_degree"]),
        "wind_direction": to_wind_direction(raw["wind_direction"]),
        "sunrise": to_time(raw["sunrise"]),
        "air_quality_carbon_monoxide": to_pollutant(raw["air_quality_Carbon_Monoxide"]),
        "air_quality_ozone": to_pollutant(raw["air_quality_Ozone"]),
        "air_quality_nitrogen_dioxide": to_pollutant(raw["air_quality_Nitrogen_dioxide"]),
        "air_quality_sulphur_dioxide": to_pollutant(raw["air_quality_Sulphur_dioxide"]),
        "air_quality_pm2_5": to_pollutant(raw["air_quality_PM2.5"]),
        "air_quality_pm10": to_pollutant(raw["air_quality_PM10"]),
        "air_quality_us_epa_index": to_int(raw["air_quality_us-epa-index"]),
        "air_quality_gb_defra_index": to_int(raw["air_quality_gb-defra-index"]),
    }
    if not row["country"] or not row["location_name"] or row["last_updated"] is None:
        return None
    return row

class CsvWeatherReader:
    def __init__(self, path: Path):
        self.path = path
        self.skipped = 0
        self.total_columns = 0

    def read(self):
        with open(self.path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            self.total_columns = len(reader.fieldnames)
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(f"У CSV немає колонок: {missing}")
            for raw in reader:
                row = convert_row(raw)
                if row is None:
                    self.skipped += 1
                else:
                    yield row