import logging
import sys
from contextlib import closing
from stravalib.exc import RateLimitExceeded
from utils import SyncDatabase, ActivityStatus, RunStatus, SyncCounts
from utils import GarminClient
from utils import StravaClient, StravaActivity
from utils import DATA_DIR, ACTIVITIES_DIR, ACTIVITY_LIMIT, DB_PATH, setup_logging


def sync_activities(database: SyncDatabase, counts: SyncCounts) -> None:
    strava_client = StravaClient(DATA_DIR, ACTIVITIES_DIR)
    garmin_client = GarminClient(DATA_DIR)

    activities = strava_client.get_latest_activities(ACTIVITY_LIMIT)
    counts.fetched = len(activities)

    logging.info("Processing activities...")
    for summary in activities:
        # Known activities are skipped before any further Strava API call
        if not database.should_process(summary.id):
            continue
        counts.new += 1

        # One broken activity must not block the rest, it is retried on the next run
        try:
            if not strava_client.is_supported(summary):
                database.set_activity_status(summary.id, ActivityStatus.SKIPPED, summary.sport_type.root, summary.start_date)
                counts.skipped += 1
                continue

            activity = StravaActivity.from_summary(summary)
            activity_file = strava_client.download_activity_file(activity)
            if activity_file and garmin_client.upload_activity(activity_file):
                database.set_activity_status(activity.id, ActivityStatus.UPLOADED, activity.type, activity.start_date)
                counts.uploaded += 1
            else:
                database.set_activity_status(activity.id, ActivityStatus.FAILED, activity.type, activity.start_date,
                                             error="FIT conversion or Garmin upload failed, see log")
                counts.failed += 1
        except RateLimitExceeded:
            # Every following call would fail too, so end the run here
            raise
        except Exception as e:
            logging.exception(f"Failed to process activity {summary.id}")
            database.set_activity_status(summary.id, ActivityStatus.FAILED, error=str(e))
            counts.failed += 1

    logging.info("All files have been processed.")


def batch_convert_fit_files() -> None:
    # closing() also closes the connection when sys.exit() ends a failed run
    with closing(SyncDatabase(DB_PATH)) as database:
        run_id = database.start_run()
        counts = SyncCounts()

        try:
            sync_activities(database, counts)
        except Exception as e:
            logging.exception("Sync run failed")
            database.finish_run(run_id, RunStatus.FAILED, counts, error=str(e))
            sys.exit(1)

        database.finish_run(run_id, RunStatus.OK, counts)
        logging.info(f"Sync run finished: {counts}")


if __name__ == '__main__':
    setup_logging()
    batch_convert_fit_files()
