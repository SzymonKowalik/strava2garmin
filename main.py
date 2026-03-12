import os
import glob
from utils import FitConverter
from utils import ActivityRegistry

def batch_convert_fit_files():
    input_dir = 'original'
    output_dir = 'processed'
    registry_path = 'activity_registry.json'

    activity_registry = ActivityRegistry(registry_path)

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    fit_files = glob.glob(os.path.join(input_dir, '*.fit'))

    # Loop through original directory
    if not fit_files:
        print(f"No .fit files found in '{input_dir}'.")
        return

    for file_path in fit_files:
        filename = os.path.basename(file_path)

        # Avoid duplicates
        if activity_registry.is_processed(file_path):
            print(f"{filename} is already processed.")
            continue

        # Convert and save hash
        output_path = os.path.join(output_dir, filename)
        if FitConverter.convert(file_path, output_path):
            activity_registry.add_activity(file_path)
            activity_registry.save()

if __name__ == '__main__':
    batch_convert_fit_files()