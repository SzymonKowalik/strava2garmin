from utils import ActivityRegistry
from utils import GarminClient
from utils import StravaClient
from utils import DATA_DIR, ACTIVITIES_DIR, ACTIVITY_LIMIT, REGISTRY_PATH

def batch_convert_fit_files():
    # Authenticate with data sources
    strava_client = StravaClient(DATA_DIR, ACTIVITIES_DIR)
    garmin_client = GarminClient(DATA_DIR)

    # Loop through activities
    activities = strava_client.get_filtered_activities(ACTIVITY_LIMIT)
    activity_registry = ActivityRegistry(REGISTRY_PATH)
    
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
