import os
import glob
from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.data_message import DataMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage


def batch_convert_fit_files():
    input_dir = 'original'
    output_dir = 'processed'

    # Garmin specific IDs
    GARMIN_MANUFACTURER_ID = 1
    FR955_PRODUCT_ID = 4024

    os.makedirs(output_dir, exist_ok=True)
    fit_files = glob.glob(os.path.join(input_dir, '*.fit'))

    if not fit_files:
        print(f"No .fit files found in '{input_dir}'.")
        return

    print(fit_files)

    for file_path in fit_files:
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)

        print(f"Processing: {filename}")

        try:
            fit_file = FitFile.from_file(file_path)
            builder = FitFileBuilder(auto_define=True)

            for record in fit_file.records:
                message = record.message

                if not isinstance(message, DataMessage):
                    continue

                # FileIdMessage
                if message.global_id == FileIdMessage.ID:
                    new_msg = FileIdMessage()
                    for field in message.fields:
                        if field.is_valid():
                            target_field = new_msg.get_field(field.field_id)
                            if target_field:
                                target_field.set_value(0, field.get_value(), None)

                    new_msg.manufacturer = GARMIN_MANUFACTURER_ID
                    new_msg.product = FR955_PRODUCT_ID
                    builder.add(new_msg)

                # DeviceInfoMessage
                elif message.global_id == DeviceInfoMessage.ID:
                    new_msg = DeviceInfoMessage()
                    for field in message.fields:
                        if field.is_valid():
                            target_field = new_msg.get_field(field.field_id)
                            if target_field:
                                target_field.set_value(0, field.get_value(), None)

                    new_msg.manufacturer = GARMIN_MANUFACTURER_ID
                    new_msg.product = FR955_PRODUCT_ID
                    new_msg.garmin_product = FR955_PRODUCT_ID
                    builder.add(new_msg)

                else:
                    builder.add(message)

            modified_file = builder.build()
            modified_file.to_file(output_path)
            print(f" -> Successfully saved to {output_path}")

        except Exception as e:
            print(f" -> Error processing {filename}: {e}")


if __name__ == '__main__':
    batch_convert_fit_files()