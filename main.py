from pathlib import Path
from dotenv import load_dotenv
from utils import ActivityRegistry
from utils import GarminClient
from utils import StravaClient

def batch_convert_fit_files():
    # Load last X strava activities
    activity_limit = 25

    # Configure paths
    activities_dir = Path('activities')
    data_dir = Path('data')
    registry_file = 'activity_registry.json'

    # Load .env variables
    load_dotenv()

    activities_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    registry_path = data_dir / registry_file
    activity_registry = ActivityRegistry(registry_path)

    # Authenticate with data sources
    strava_client = StravaClient(data_dir, activities_dir)
    garmin_client = GarminClient(data_dir)

    # Loop through activities
    activities = strava_client.get_filtered_activities(activity_limit)

    print("Processing activities...")
    for activity in activities:
        if activity_registry.is_processed(str(activity.id)):
            continue

        # Upload activities
        activity_file = strava_client.download_activity_file(activity)
        if activity_file and garmin_client.upload_activity(activity_file):
            activity_registry.mark_processed(str(activity.id))

    print("All files have been processed.")
if __name__ == '__main__':
    batch_convert_fit_files()
