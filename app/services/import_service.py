from app.services.csv_reader import CsvWeatherReader

class ImportService:
    def __init__(self, repository, batch_size: int = 5000):
        self.repository= repository
        self.batch_size= batch_size

    def import_csv(self, path, replace: bool = False) -> dict:
        existing= self.repository.count()
        if existing and not replace:
            raise RuntimeError(
                f"У таблиці вже {existing} рядків. Запусти з --replace, щоб перезавантажити."
            )
        if existing:
            self.repository.delete_all()

        reader =CsvWeatherReader(path)
        inserted =0
        batch =[]
        for row in reader.read():
            batch.append(row)
            if len(batch) == self.batch_size:
                inserted += self.repository.bulk_insert(batch)
                batch = []
                print(f"  вставлено {inserted}", end="\r")
        inserted += self.repository.bulk_insert(batch)

        return {
            "total_columns": reader.total_columns,
            "inserted": inserted,
            "skipped": reader.skipped,
        }