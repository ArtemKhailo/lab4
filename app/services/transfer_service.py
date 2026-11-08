from app.models import AirQuality, Weather

TABLES=[Weather.__table__, AirQuality.__table__]

class TransferError(Exception):
    pass

class TransferService:
    def __init__(self, source, target, batch_size: int = 5000):
        self.source = source
        self.target = target
        self.batch_size = batch_size

    def transfer(self) -> dict:
        for table in TABLES:
            if self.target.count(table):
                raise TransferError(f"У цільовій базі таблиця {table.name} не порожня.")

        result = {}
        for table in TABLES:
            copied = 0
            for rows in self.source.read_batches(table, self.batch_size):
                self.target.insert(table, rows)
                copied += len(rows)
                print(f"  {table.name}: {copied}", end="\r")
            print()
            result[table.name] = (self.source.count(table), self.target.count(table))
        return result