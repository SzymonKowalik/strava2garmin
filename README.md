## strava2garmin

### Description
Processes `.fit` files downloaded from strava and changes fields: manufacturer (garmin) and product (fr955).
It makes those files compatible with Garmin's training features. 
Currently, all files must be downloaded separately from strava, but can be uploaded together on Garmin Connect.

### Compatibility
Tested with Virtual Rides from:
- BikeTerra
- MyWhoosh
- Rouvy

### Usage
Install required dependencies
`pip install -r requirements.txt`<br>
Place activities from strava into `original` directory<br>
Run program `python main.py`<br>
Upload files from `processed` directory to Garmin Connect