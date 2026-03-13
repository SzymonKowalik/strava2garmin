from pathlib import Path
from dotenv import load_dotenv
from utils import FitConverter
from utils import ActivityRegistry
from utils import GarminClient

def batch_convert_fit_files():
    # Configure paths
    input_dir = Path('original')
    output_dir = Path('processed')
    data_dir = Path('data')
    registry_file = 'activity_registry.json'

    # Load .env variables
    load_dotenv()

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    fit_files = list(Path(input_dir).glob('*.fit'))

    registry_path = data_dir / registry_file
    activity_registry = ActivityRegistry(registry_path)
    garmin_client = GarminClient(data_dir)

    # Loop through original directory
    if not fit_files:
        print(f"No .fit files found in '{input_dir}'.")
        return

    for file_path in fit_files:
        filename = file_path.name

        # Avoid duplicates
        if activity_registry.is_processed(file_path):
            print(f"{filename} is already processed.")
            continue

        # Convert, add hash and upload
        output_path = output_dir / filename
        if FitConverter.convert(file_path, output_path):
            if garmin_client.upload_activity(output_path):
                activity_registry.add_activity(file_path)
                activity_registry.save()

if __name__ == '__main__':
    batch_convert_fit_files()