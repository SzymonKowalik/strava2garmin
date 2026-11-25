import garth
from garth.exc import GarthHTTPError
from pathlib import Path
from .config import require_env

class GarminClient:
    def __init__(self, data_dir: Path):
        self.garth_path: Path = data_dir / ".garth"
        self._authenticate()

    def _login(self):
        # Login to Garmin Connect
        garth.login(require_env('GARMIN_LOGIN'), require_env('GARMIN_PASSWORD'))
        garth.save(self.garth_path)
        print("Garmin - Login successful")

    def _authenticate(self):
        try:
            garth.resume(self.garth_path)
            print("Garmin - Session resumed")
        except Exception as e:
            print(f"Garmin - Could not resume session ({e}). Logging in...")
            self._login()

    @staticmethod
    def upload_activity(file_path: Path) -> bool:
        try:
            with open(file_path, "rb") as f:
                garth.client.upload(f)
            print("Garmin - Activity upload successful")
            return True
        except GarthHTTPError as e:
            status_code = e.error.response.status_code
            if status_code == 409:
                print(f"Garmin - Skip: Activity already exists on Garmin Connect.")
                return True
            else:
                print(f"Garmin - Garmin API Error ({status_code}): {e}")
                return False
        except Exception as e:
            print(f"Garmin - Unexpected error: {e}")
            return False