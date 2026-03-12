import os
import json
import hashlib

class ActivityRegistry:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.processed_activities: set = self.load_processed_activities()

    def load_processed_activities(self) -> set:
        # Create if not exists or load file data
        if not os.path.exists(self.file_path):
            return set()

        try:
            with open(self.file_path, "r", encoding="UTF-8") as f:
                data = json.load(f)
                return set(data)
        except (json.JSONDecodeError, OSError):
            return set()

    @staticmethod
    def _generate_hash(file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def is_processed(self, file_path: str) -> bool:
        return self._generate_hash(file_path) in self.processed_activities

    def add_activity(self, file_path: str) -> None:
        self.processed_activities.add(self._generate_hash(file_path))

    def save(self) -> None:
        with open(self.file_path, "w", encoding="UTF-8") as f:
            json.dump(list(self.processed_activities), f)
