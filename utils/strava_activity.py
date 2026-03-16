from datetime import datetime

class StravaActivity:
    def __init__(self, activity_id: int, start_date: datetime, kilojoules: float):
        self.id: int = activity_id
        self.start_date: datetime = start_date
        self.calories: float = kilojoules # Roughly 1 kcal = 1kJ for cycling
