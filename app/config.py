import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT=Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL= os.getenv("DATABASE_URL")

CSV_PATH= PROJECT_ROOT / os.getenv("CSV_PATH", "data/GlobalWeatherRepository.csv")