import os
import json
from datetime import datetime
from pathlib import Path
from stravalib.client import Client
from urllib.parse import urlparse, parse_qs
from . import FitConverter

class StravaActivity:
    def __init__(self, activity_id: int, start_date: datetime):
        self.id: int = activity_id
        self.start_date: datetime = start_date

class StravaClient:
    def __init__(self, data_dir: Path, input_dir: Path):
        self.input_dir: Path = input_dir

        self.strava_dir: Path = data_dir / Path("strava")
        self.strava_dir.mkdir(parents=True, exist_ok=True)

        self.token_path: Path = self.strava_dir / ".strava_token.json"

        self.client_id: int = int(os.getenv("STRAVA_CLIENT_ID"))
        self.client_secret: str = os.getenv("STRAVA_CLIENT_SECRET")

        self.client: Client = self._authenticate()

    def _save_token(self, token_response: dict) -> None:
        data: dict = {
            "access_token": token_response.get("access_token"),
            "refresh_token": token_response.get("refresh_token"),
        }

        with open(self.token_path, "w") as f:
            json.dump(data, f)

    def _load_token(self) -> dict:
        try:
            with open(self.token_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def _parse_url(url: str) -> str:
        parsed_url = urlparse(url)
        params_dict = parse_qs(parsed_url.query)
        return params_dict.get('code', [None])[0]


    def _establish_session(self) -> Client:
        print("Strava - Session could be restored")
        client = Client()

        # Get authorization code
        authorize_url = client.authorization_url(
            client_id = self.client_id,
            redirect_uri = 'http://127.0.0.1:5080/authorization',
            scope = ['read_all', 'activity:read_all']
        )
        print(f"Strava - Click here to authorize to strava account: {authorize_url}")
        callback_url = input("Strava - Then copy and paste the entire url here: ")

        code = self._parse_url(callback_url)
        if not code:
            raise ValueError("Strava - Code not found in the callback url")

        # Exchange for token
        token_response = client.exchange_code_for_token(
            client_id = self.client_id,
            client_secret= self.client_secret,
            code = code
        )

        if not token_response.get("refresh_token"):
            raise ValueError("Strava - Refresh token was not obtained")

        self._save_token(token_response)

        print("Strava - User logged in successfully")

        return client

    def _authenticate(self) -> Client:
        print("Strava - Restoring user session")
        token_dict = self._load_token()

        if not token_dict:
            return self._establish_session()

        client = Client()
        token_response = client.refresh_access_token(
            client_id = self.client_id,
            client_secret = self.client_secret,
            refresh_token = token_dict.get("refresh_token"),
        )

        if not token_response:
            return self._establish_session()

        print("Strava - User logged in successfully")
        return client

    def get_filtered_activities(self, limit=25) -> list[StravaActivity]:
        print(f"Strava - Fetching latest {limit} activities")
        activities = self.client.get_activities(limit=limit)
        filtered_activities: list[StravaActivity] = []

        for activity in activities:
            if activity.sport_type.root != "VirtualRide":
                continue

            filtered_activities.append(
                StravaActivity(activity.id, activity.start_date)
            )

        print(f"Strava - Activities fetched and filtered")
        return filtered_activities


    def download_activity_file(self, activity: StravaActivity) -> Path|None:
        types = ["latlng", "altitude", "time", "distance", "velocity_smooth", "heartrate", "cadence", "watts", "moving", "grade_smooth"]
        streams = self.client.get_activity_streams(
            activity_id=activity.id,
            types=types,
            resolution=None,
        )

        # Convert Stream objects to a serializable dictionary
        serializable_data = {
            key: stream.data for key, stream in streams.items()
        }

        file_path = self.input_dir / f"{activity.id}.fit"

        print(f"Strava - Downloading activity with id: {activity.id}")
        if FitConverter.create_from_streams(serializable_data, activity.start_date, file_path):
            return file_path

        else:
            return None
