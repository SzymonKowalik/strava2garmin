import json
from pathlib import Path

class ActivityRegistry:
    def __init__(self, file_path: Path):
        self.file_path: Path = file_path
        self.processed_activities: dict = self.load_processed_activities()

    def load_processed_activities(self) -> dict:
        # Create if not exists or load file data
        if not self.file_path.exists():
            return dict()

        try:
            with open(self.file_path, "r", encoding="UTF-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return dict()

    def is_processed(self, activity_id: str) -> bool:
        is_processed = self.processed_activities.get(activity_id)

        if not is_processed:
            self.processed_activities[activity_id] = False

        return is_processed

    def mark_processed(self, activity_id: str) -> None:
        self.processed_activities[activity_id] = True
        self._save()

    def _save(self) -> None:
        with open(self.file_path, "w", encoding="UTF-8") as f:
            json.dump(self.processed_activities, f)
