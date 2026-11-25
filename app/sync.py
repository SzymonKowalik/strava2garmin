import sys
from stravalib.exc import RateLimitExceeded
from utils import ActivityRegistry
from utils import GarminClient
from utils import StravaClient
from utils import DATA_DIR, ACTIVITIES_DIR, ACTIVITY_LIMIT, REGISTRY_PATH

def batch_convert_fit_files():
    try:
        # Authenticate with data sources
        strava_client = StravaClient(DATA_DIR, ACTIVITIES_DIR)
        garmin_client = GarminClient(DATA_DIR)
    except Exception as e:
        print(f"Could not connect to services. Error message: {e}")
        sys.exit(1)

    # Loop through activities
    activities = strava_client.get_filtered_activities(ACTIVITY_LIMIT)
    activity_registry = ActivityRegistry(REGISTRY_PATH)
    
    print("Processing activities...")
    for activity in activities:
        if activity_registry.is_processed(str(activity.id)):
            continue

        # One broken activity must not block the rest, it is retried on the next run
        try:
            activity_file = strava_client.download_activity_file(activity)
            if activity_file and garmin_client.upload_activity(activity_file):
                activity_registry.mark_processed(str(activity.id))
        except RateLimitExceeded:
            print("Strava - Rate limit reached, stopping until the next run")
            break
        except Exception as e:
            print(f"Failed to process activity {activity.id}: {e}")

    print("All files have been processed.")

if __name__ == '__main__':
    batch_convert_fit_files()
