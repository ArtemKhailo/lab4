import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT=Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

POSTGRES_URL =os.getenv("POSTGRES_URL")
MYSQL_URL =os.getenv("MYSQL_URL")
DB =os.getenv("DB", "postgres")

DATABASE_URL =MYSQL_URL if DB == "mysql" else POSTGRES_URL

CSV_PATH= PROJECT_ROOT / os.getenv("CSV_PATH", "data/GlobalWeatherRepository.csv")