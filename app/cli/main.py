import argparse
from app.config import CSV_PATH
from app.db import SessionLocal
from app.repositories.weather_repository import WeatherRepository
from app.services.import_service import ImportService

def cmd_import(args):
    service = ImportService(WeatherRepository(SessionLocal))
    print(f"Читаю {CSV_PATH} ...")
    result = service.import_csv(CSV_PATH, replace=args.replace)
    print()
    print(f"Колонок у CSV: {result['total_columns']}, у моделі: 17")
    print(f"Вставлено: {result['inserted']}, пропущено: {result['skipped']}")

def cmd_stats(args):
    repo = WeatherRepository(SessionLocal)
    s = repo.summary()
    print(f"Рядків: {s['total']}, країн: {s['countries']}")
    print(f"Період: {s['first']} -> {s['last']}\n")
    for w in repo.sample(args.limit):
        print(
            f"{w.id:>3} | {w.country:<12.12} | {w.last_updated:%Y-%m-%d %H:%M} | "
            f"вітер {w.wind_kph} км/год {w.wind_degree}° {w.wind_direction.value} | "
            f"схід {w.sunrise:%H:%M} | PM2.5 {w.air_quality.pm2_5}"
        )

def run():
    parser = argparse.ArgumentParser(description="Погодна БД")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("import", help="завантажити CSV у таблицю weather")
    p.add_argument("--replace", action="store_true", help="очистити таблицю перед імпортом")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("stats", help="показати статистику і перші рядки")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)