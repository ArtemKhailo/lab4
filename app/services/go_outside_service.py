EPA_UNHEALTHY=4      
PM25_LIMIT=55.4      

def is_safe_to_go_outside(pm2_5, us_epa_index):
    """True - можна виходити, False - краще не виходити, None - немає даних."""
    if pm2_5 is None and us_epa_index is None:
        return None
    if us_epa_index is not None and us_epa_index >= EPA_UNHEALTHY:
        return False
    if pm2_5 is not None and pm2_5 > PM25_LIMIT:
        return False
    return True

class GoOutsideService:
    def __init__(self, repository, batch_size: int = 5000):
        self.repository = repository
        self.batch_size = batch_size

    def fill(self) -> dict:
        counts = {True: 0, False: 0, None: 0}
        for batch in self.repository.air_quality_batches(self.batch_size):
            values = []
            for row in batch:
                answer = is_safe_to_go_outside(row.pm2_5, row.us_epa_index)
                counts[answer] += 1
                values.append({"id": row.id, "is_safe_to_go_outside": answer})
            self.repository.update_go_outside(values)
        return counts