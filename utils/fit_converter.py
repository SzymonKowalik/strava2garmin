from datetime import datetime
from pathlib import Path
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.sport_message import SportMessage


class FitConverter:
    @staticmethod
    def create_from_streams(streams: dict, start_date: datetime, output_path: Path) -> bool:
        builder = FitFileBuilder(auto_define=True)
        start_timestamp_ms = int(start_date.timestamp() * 1000)

        # Setup Device
        file_id = FileIdMessage()
        file_id.manufacturer = 1  # Garmin
        file_id.product = 4024  # FR955
        file_id.type = 4  # Activity
        file_id.time_created = start_timestamp_ms
        builder.add(file_id)

        device = DeviceInfoMessage()
        device.timestamp = start_timestamp_ms
        device.manufacturer = 1  # Garmin
        device.product = 4024  # FR955
        device.serial_number = 1234567890
        builder.add(device)

        # Sport Message defines the type of activity
        sport = SportMessage()
        sport.sport = 2  # Cycling
        sport.sub_sport = 58  # Virtual
        sport.name = "Virtual Cycling"
        builder.add(sport)

        # Iterate through stream data
        num_records = len(streams['time'])

        for i in range(num_records):
            record = RecordMessage()

            elapsed_ms = int(streams['time'][i] * 1000)
            record.timestamp = start_timestamp_ms + elapsed_ms

            if 'latlng' in streams:
                record.position_lat = streams['latlng'][i][0]
                record.position_long = streams['latlng'][i][1]

            if 'altitude' in streams:
                record.altitude = streams['altitude'][i]

            if 'heartrate' in streams:
                record.heart_rate = int(streams['heartrate'][i])

            if 'watts' in streams:
                record.power = int(streams['watts'][i])

            if 'cadence' in streams:
                record.cadence = int(streams['cadence'][i])

            if 'velocity_smooth' in streams:
                record.speed = streams['velocity_smooth'][i]

            if 'distance' in streams:
                record.distance = streams['distance'][i]

            if 'grade_smooth' in streams:
                record.grade = streams['grade_smooth'][i]

            builder.add(record)

        # Create activity summary
        total_elapsed = streams['time'][-1]  # Last timestamp

        session = SessionMessage()
        session.timestamp = start_timestamp_ms + int(total_elapsed * 1000)
        session.start_time = start_timestamp_ms
        session.total_elapsed_time = total_elapsed
        session.total_timer_time = total_elapsed
        if 'distance' in streams:
            session.total_distance = streams['distance'][-1]
        if 'watts' in streams:
            session.avg_power = sum(streams['watts']) / len(streams['watts'])  # Simple average
        session.sport = 2
        session.sub_sport = 58
        builder.add(session)

        activity_msg = ActivityMessage()
        activity_msg.timestamp = start_timestamp_ms + int(total_elapsed * 1000)
        activity_msg.num_sessions = 1
        activity_msg.type = 0
        builder.add(activity_msg)

        # Build and Save
        try:
            fit_file = builder.build()
            fit_file.to_file(str(output_path))
            return True
        except Exception as e:
            print(f"Failed to create FIT file: {e}")
            return False