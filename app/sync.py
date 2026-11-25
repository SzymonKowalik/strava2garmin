import logging
import sys
from stravalib.exc import RateLimitExceeded
from utils import SyncDatabase, ActivityStatus
from utils import GarminClient
from utils import StravaClient
from utils import DATA_DIR, ACTIVITIES_DIR, ACTIVITY_LIMIT, DB_PATH, setup_logging

def batch_convert_fit_files():
    try:
        # Authenticate with data sources
        strava_client = StravaClient(DATA_DIR, ACTIVITIES_DIR)
        garmin_client = GarminClient(DATA_DIR)
    except Exception as e:
        logging.error(f"Could not connect to services. Error message: {e}")
        sys.exit(1)

    # Loop through activities
    activities = strava_client.get_filtered_activities(ACTIVITY_LIMIT)
    database = SyncDatabase(DB_PATH)
    
    logging.info("Processing activities...")
    for activity in activities:
        if not database.should_process(activity.id):
            continue

        # One broken activity must not block the rest, it is retried on the next run
        try:
            activity_file = strava_client.download_activity_file(activity)
            if activity_file and garmin_client.upload_activity(activity_file):
                database.set_activity_status(
                    activity.id, ActivityStatus.UPLOADED, activity.type, activity.start_date
                )
        except RateLimitExceeded:
            logging.warning("Strava - Rate limit reached, stopping until the next run")
            break
        except Exception:
            logging.exception(f"Failed to process activity {activity.id}")

    logging.info("All files have been processed.")

if __name__ == '__main__':
    setup_logging()
    batch_convert_fit_files()
