## strava2garmin

### Description
Downloads Cycling Virtual Rides and Rides from Strava and adds Garmin device info: manufacturer (garmin) and product (fr955).
It makes those files compatible with Garmin's training features.

### Compatibility
Works with:
- Virtual Rides (BikeTerra, MyWhoosh, Rouvy, etc.)
- Rides (iGPSPORT bike computer)

### Usage
1. Create a [Strava API application](https://developers.strava.com/docs/getting-started/#account).
2. To authenticate with Strava and Garmin, create environment variables or `.env` file with content from `.env.example` file in the `app` folder.
3. Install required dependencies `pip install -r requirements.txt`
##### Manual
4. To manually run program use `python app/sync.py`
##### Automated
4. Run `python app/authenticate.py` and follow instructions to allow access to Strava activities.
5. Run `docker compose up` to start the service. It automatically synchronizes activities every hour.

**Note:** On the first run you will need to follow instructions to allow access to Strava activities.<br><br>
All activities will automatically be uploaded to Garmin Connect (Be aware, if you already had uploaded 
activity manually, a duplicate will be created!)

### Configuration
In `app/utils/config.py` you can change the default values for activity count and file paths.

### Future Improvements
- Improve Docker first time setup