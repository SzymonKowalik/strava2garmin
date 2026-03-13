import garth
import os
from garth.exc import GarthHTTPError
from pathlib import Path


class GarminClient:
    def __init__(self, data_dir: Path):
        self.garth_path: Path = data_dir / ".garth"
        self.authenticate()

    def login(self):
        # Login to Garmin Connect
        login = os.getenv('GARMIN_LOGIN')
        password = os.getenv('GARMIN_PASSWORD')

        if not login or not password:
            raise KeyError("Could not find GARMIN_LOGIN and/or GARMIN_PASSWORD variable")

        garth.login(login, password)
        garth.save(self.garth_path)
        print("Garmin Connect login successful")

    def authenticate(self):
        try:
            garth.resume(self.garth_path)
            print("Garmin Connect session resumed")
        except:
            print("Could not resume Garmin Connect session. Logging in...")
            self.login()

    @staticmethod
    def upload_activity(file_path: Path) -> bool:
        try:
            with open(file_path, "rb") as f:
                garth.client.upload(f)
            print(" -> Activity upload successful")
            return True
        except GarthHTTPError as e:
            status_code = e.error.response.status_code
            if status_code == 409:
                print(f" -> Skip: Activity already exists on Garmin Connect.")
                return True
            else:
                print(f" -> Garmin API Error ({status_code}): {e}")
                return False
        except Exception as e:
            print(f" -> Unexpected error: {e}")
            return False