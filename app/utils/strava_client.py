import logging
import json
import sys
from pathlib import Path
from stravalib.client import Client
from stravalib.model import SummaryActivity
from urllib.parse import urlparse, parse_qs
from .config import require_env
from .fit_converter import FitConverter
from .strava_activity import StravaActivity

class StravaClient:
    def __init__(self, data_dir: Path, input_dir: Path):
        self.input_dir: Path = input_dir

        self.strava_dir: Path = data_dir / Path("strava")
        self.strava_dir.mkdir(parents=True, exist_ok=True)

        self.token_path: Path = self.strava_dir / "strava_token.json"

        self.client_id: int = int(require_env("STRAVA_CLIENT_ID"))
        self.client_secret: str = require_env("STRAVA_CLIENT_SECRET")

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
        logging.warning("Strava - Session could not be restored")
        # Authorizing needs a person to open the link, which is impossible in the Docker loop
        if not sys.stdin.isatty():
            raise RuntimeError("Strava - Not authorized. Run `python app/authenticate.py` first.")

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

        logging.info("Strava - User logged in successfully")

        return client

    def _authenticate(self) -> Client:
        logging.info("Strava - Restoring user session")
        token_dict = self._load_token()

        if not token_dict:
            return self._establish_session()

        client = Client()
        try:
            token_response = client.refresh_access_token(
                client_id = self.client_id,
                client_secret = self.client_secret,
                refresh_token = token_dict.get("refresh_token"),
            )
        except Exception as e:
            logging.warning(f"Strava - Token refresh failed: {e}")
            return self._establish_session()

        # Strava can rotate the refresh token, so always keep the latest one
        self._save_token(token_response)
        logging.info("Strava - User logged in successfully")
        return client

    def get_latest_activities(self, limit: int) -> list[SummaryActivity]:
        # One API call returns summaries of the newest activities
        logging.info(f"Strava - Fetching latest {limit} activities")
        return list(self.client.get_activities(limit=limit))

    def is_supported(self, activity: SummaryActivity) -> bool:
        # Zwift uploads to Garmin Connect natively
        if (activity.external_id or "").startswith('zwift'):
            return False

        sport_type = activity.sport_type.root
        if sport_type == "VirtualRide":
            return True
        if sport_type == "Ride":
            # device_name is only on the detailed activity, which costs one extra API call.
            # It is None for rides recorded without a device (e.g. manual entries).
            device_name = self.client.get_activity(activity.id).device_name or ""
            return "igpsport" in device_name.lower()
        return False

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

        logging.info(f"Strava - Downloading activity with id: {activity.id}")
        if FitConverter.create_from_streams(serializable_data, activity, file_path):
            return file_path

        else:
            return None
