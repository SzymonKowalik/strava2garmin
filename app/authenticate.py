from utils import GarminClient, StravaClient, DATA_DIR, ACTIVITIES_DIR, setup_logging

def main():
    setup_logging()
    # Authenticates, raises errors on failure
    StravaClient(DATA_DIR, ACTIVITIES_DIR)
    GarminClient(DATA_DIR)

    print("Authenticated. You can now safely run recurring job.")

if __name__ == "__main__":
    main()