import argparse
from app.config import CSV_PATH
from app.db import SessionLocal
from app.repositories.weather_repository import WeatherRepository
from app.services.import_service import ImportService
from app.services.go_outside_service import GoOutsideService
from app.services.search_service import SearchError, SearchService

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

def cmd_fill_go_outside(args):
    service = GoOutsideService(WeatherRepository(SessionLocal))
    counts = service.fill()
    print(f"Так: {counts[True]}, ні: {counts[False]}, немає даних: {counts[None]}")

def yes_no(value):
    return {True: "ТАК", False: "НІ", None: "немає даних"}[value]

def cmd_search(args):
    service = SearchService(WeatherRepository(SessionLocal))
    try:
        country, records = service.search(args.country, args.date, args.city)
    except SearchError as e:
        print(e)
        return

    print(f"\n{country}, {args.date}: знайдено записів: {len(records)}")
    for w in records:
        a = w.air_quality
        print("\n" + "=" * 50)
        print(f"{w.location_name}, оновлено о {w.last_updated:%H:%M}")
        print("=" * 50)
        print(f"Погода:       {w.condition_text}, {w.temperature_celsius} °C")
        print(f"Вітер:        {w.wind_kph} км/год, {w.wind_degree}°, напрямок {w.wind_direction.value}")
        print(f"Схід сонця:   {w.sunrise:%H:%M}")
        print("Якість повітря:")
        print(f"  CO:         {a.carbon_monoxide} мкг/м³")
        print(f"  O3:         {a.ozone} мкг/м³")
        print(f"  NO2:        {a.nitrogen_dioxide} мкг/м³")
        print(f"  SO2:        {a.sulphur_dioxide} мкг/м³")
        print(f"  PM2.5:      {a.pm2_5} мкг/м³")
        print(f"  PM10:       {a.pm10} мкг/м³")
        print(f"  US EPA:     {a.us_epa_index} (1 - добре ... 6 - небезпечно)")
        print(f"  UK DEFRA:   {a.gb_defra_index} (1 - низький ... 10 - дуже високий)")
        print(f"Чи варто виходити на вулицю: {yes_no(a.is_safe_to_go_outside)}")

def cmd_countries(args):
    repo = WeatherRepository(SessionLocal)
    names = repo.countries()
    print(f"Країн у базі: {len(names)}\n")
    print(", ".join(names))

def run():
    parser = argparse.ArgumentParser(description="Погодна БД")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("import", help="завантажити CSV у таблицю weather")
    p.add_argument("--replace", action="store_true", help="очистити таблицю перед імпортом")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("stats", help="показати статистику і перші рядки")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("fill-go-outside", help="заповнити колонку 'Чи варто виходити на вулицю'")
    p.set_defaults(func=cmd_fill_go_outside)

    p = sub.add_parser("search", help="погода за країною і датою")
    p.add_argument("country", help="назва країни англійською, напр. Ukraine")
    p.add_argument("date", help="дата у форматі РРРР-ММ-ДД")
    p.add_argument("--city", help="місто (необов'язково)")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("countries", help="список країн у базі")
    p.set_defaults(func=cmd_countries)

    args = parser.parse_args()
    args.func(args)

