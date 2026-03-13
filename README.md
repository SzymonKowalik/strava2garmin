## strava2garmin

### Description
Processes `.fit` files downloaded from strava and changes fields: manufacturer (garmin) and product (fr955).
It makes those files compatible with Garmin's training features. 
Currently, all files must be downloaded manually from strava, but are automatically uploaded to Garmin Connect.

### Compatibility
Tested with Virtual Rides from:
- BikeTerra
- MyWhoosh
- Rouvy

### Usage
To authenticate with Garmin set up environmental variables or .env file (in the project root):
```
GARMIN_LOGIN=
GARMIN_PASSWORD=
```
Install required dependencies
`pip install -r requirements.txt`<br>
Place activities from strava into `original` directory<br>
Run program `python main.py`<br>
Upload files from `processed` directory to Garmin Connect