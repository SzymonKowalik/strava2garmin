import garth
import os

from garth.exc import GarthHTTPError


class GarminClient:
    def __init__(self, data_dir: str):
        self.garth_path = os.path.join(data_dir, ".garth")
        self.authenticate()

    def login(self):
        # Login to Garmin Connect
        login = os.getenv('GARMIN_LOGIN')
        password = os.getenv('GARMIN_PASSWORD')

        if not login or not password:
            raise KeyError("Could not find GARMIN_LOGIN and/or GARMIN_PASSWORD variable")

        garth.login(login, password)
        garth.save(self.garth_path)
        print("Garmin login successful")

    def authenticate(self):
        try:
            garth.resume(self.garth_path)
            print("Garmin login successful")
        except:
            print("Could not resume Garmin session. Logging in...")
            self.login()

    @staticmethod
    def upload_activity(file_path: str) -> bool:
        try:
            with open(file_path, "rb") as f:
                garth.client.upload(f)
            print(" -> Activity upload successful")
            return True
        except GarthHTTPError as e:
            status_code = e.error.response.status_code
            if status_code == 409:
                print(f" -> Skip: Activity already exists on Garmin.")
                return True
            else:
                print(f" -> Garmin API Error ({status_code}): {e}")
                return False
        except Exception as e:
            print(f" -> Unexpected error: {e}")
            return False