from sqlalchemy import create_engine, func, insert, select

class TableCopyRepository:
    def __init__(self, url: str):
        self.engine = create_engine(url)

    def count(self, table) -> int:
        with self.engine.connect() as conn:
            return conn.scalar(select(func.count()).select_from(table))

    def read_batches(self, table, batch_size: int):
        last_id = 0
        while True:
            with self.engine.connect() as conn:
                rows = conn.execute(
                    select(table)
                    .where(table.c.id > last_id)
                    .order_by(table.c.id)
                    .limit(batch_size)
                ).mappings().all()
            if not rows:
                break
            yield [dict(row) for row in rows]
            last_id = rows[-1]["id"]

    def insert(self, table, rows: list[dict]) -> None:
        with self.engine.begin() as conn:
            conn.execute(insert(table), rows)