from datetime import datetime
from stravalib.model import SummaryActivity

class StravaActivity:
    def __init__(self, activity_id: int, start_date: datetime, kilojoules: float, type: str):
        self.id: int = activity_id
        self.start_date: datetime = start_date
        self.calories: float = kilojoules # Roughly 1 kcal = 1kJ for cycling
        self.type: str = type

    @classmethod
    def from_summary(cls, summary: SummaryActivity) -> "StravaActivity":
        return cls(summary.id, summary.start_date, summary.kilojoules, summary.sport_type.root)
