from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.sport_message import SportMessage
from .strava_activity import StravaActivity

@dataclass(frozen=True)
class StreamField:
    """Copies one Strava stream into one field of a FIT record."""
    stream_name: str
    record_field: str
    convert: Callable[[float], float | int]


STREAM_FIELDS = (
    StreamField('altitude', 'altitude', float),
    StreamField('heartrate', 'heart_rate', int),
    StreamField('watts', 'power', int),
    StreamField('cadence', 'cadence', int),
    StreamField('velocity_smooth', 'speed', float),
    StreamField('distance', 'distance', float),
    StreamField('grade_smooth', 'grade', float),
)


def _present_values(values: list) -> list:
    # Strava streams contain None where the sensor dropped out
    return [value for value in values if value is not None]


class FitConverter:
    @staticmethod
    def create_from_streams(streams: dict, activity: StravaActivity, output_path: Path) -> bool:
        time_stream = streams.get('time')
        if not time_stream:
            print(f"Skipping activity {activity.id}: it has no time stream (manual activity?)")
            return False

        builder = FitFileBuilder(auto_define=True)
        start_timestamp_ms = int(activity.start_date.timestamp() * 1000)

        # Check activity type
        is_virtual = activity.type == "VirtualRide"
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
        sport.sub_sport = 58 if is_virtual else 0
        sport.name = "Virtual Cycling" if is_virtual else "Cycling"
        builder.add(sport)

        # Iterate through stream data
        num_records = len(time_stream)
        moving_stream = streams.get('moving', [True] * num_records)
        moving_time_seconds = moving_stream.count(True)

        for i in range(num_records):
            record = RecordMessage()
            record.timestamp = start_timestamp_ms + int(time_stream[i] * 1000)

            latlng = streams.get('latlng')
            if latlng and latlng[i] is not None:
                record.position_lat, record.position_long = latlng[i]

            for field in STREAM_FIELDS:
                stream = streams.get(field.stream_name)
                if stream and stream[i] is not None:
                    setattr(record, field.record_field, field.convert(stream[i]))

            builder.add(record)

        # Create activity summary
        total_elapsed = time_stream[-1]  # Last timestamp

        session = SessionMessage()
        session.timestamp = start_timestamp_ms + int(total_elapsed * 1000)
        session.start_time = start_timestamp_ms
        session.total_elapsed_time = total_elapsed
        session.total_timer_time = moving_time_seconds
        if activity.calories is not None:
            session.total_calories = int(activity.calories)

        distances = _present_values(streams.get('distance', []))
        if distances:
            session.total_distance = distances[-1]

        powers = _present_values(streams.get('watts', []))
        if powers:
            session.avg_power = sum(powers) / len(powers)  # Simple average

        session.sport = 2
        session.sub_sport = 58 if is_virtual else 0
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
