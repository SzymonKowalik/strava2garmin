## strava2garmin

### Description
Downloads Virtual Rides from Strava and adds Garmin device info: manufacturer (garmin) and product (fr955).
It makes those files compatible with Garmin's training features.

### Compatibility
Tested with Virtual Rides from:
- BikeTerra
- MyWhoosh
- Rouvy

### Usage
To authenticate with Strava and Garmin, create environmental variables or .env file (in the project root):
```
GARMIN_LOGIN=
GARMIN_PASSWORD=
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
```
Additionally, you will need to create Strava app in order to access API.
<br><br>
Install required dependencies
`pip install -r requirements.txt`<br>
Run program `python main.py`<br>
When executing the first time you will need to follow instructions to allow access to Strava activities.<br><br>
All activities will automatically be uploaded to Garmin Connect (Be aware, if you already had uploaded 
activity manually, there would be a duplicate!)