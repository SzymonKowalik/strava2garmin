import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

# A failed activity is retried on later runs until it has failed this many times
MAX_UPLOAD_ATTEMPTS = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS activities (
    strava_id   INTEGER PRIMARY KEY,
    sport_type  TEXT,
    start_date  TEXT,
    status      TEXT NOT NULL,
    attempts    INTEGER NOT NULL DEFAULT 0,
    last_error  TEXT,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    status      TEXT NOT NULL,
    fetched     INTEGER NOT NULL DEFAULT 0,
    new         INTEGER NOT NULL DEFAULT 0,
    uploaded    INTEGER NOT NULL DEFAULT 0,
    skipped     INTEGER NOT NULL DEFAULT 0,
    failed      INTEGER NOT NULL DEFAULT 0,
    error       TEXT
);
"""


class ActivityStatus(StrEnum):
    UPLOADED = "uploaded"
    FAILED = "failed"
    SKIPPED = "skipped"


class RunStatus(StrEnum):
    RUNNING = "running"
    OK = "ok"
    FAILED = "failed"


@dataclass
class SyncCounts:
    fetched: int = 0
    new: int = 0
    uploaded: int = 0
    skipped: int = 0
    failed: int = 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SyncDatabase:
    """Remembers which Strava activities were handled and records every sync run."""

    def __init__(self, db_path: Path):
        self._connection = sqlite3.connect(db_path)
        self._connection.executescript(SCHEMA)

    def should_process(self, strava_id: int) -> bool:
        row = self._connection.execute(
            "SELECT status, attempts FROM activities WHERE strava_id = ?", (strava_id,)
        ).fetchone()
        if row is None:
            return True
        status, attempts = row
        return status == ActivityStatus.FAILED and attempts < MAX_UPLOAD_ATTEMPTS

    def set_activity_status(
        self,
        strava_id: int,
        status: ActivityStatus,
        sport_type: str | None = None,
        start_date: datetime | None = None,
        error: str | None = None,
    ) -> None:
        failed_attempt = 1 if status == ActivityStatus.FAILED else 0
        # Each "with" block is one transaction, committed as soon as it ends
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO activities (strava_id, sport_type, start_date, status, attempts, last_error, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (strava_id) DO UPDATE SET
                    sport_type = COALESCE(excluded.sport_type, sport_type),
                    start_date = COALESCE(excluded.start_date, start_date),
                    status = excluded.status,
                    attempts = attempts + excluded.attempts,
                    last_error = excluded.last_error,
                    updated_at = excluded.updated_at
                """,
                (
                    strava_id,
                    sport_type,
                    start_date.isoformat() if start_date else None,
                    status,
                    failed_attempt,
                    error,
                    _now(),
                ),
            )

    def start_run(self) -> int:
        with self._connection:
            cursor = self._connection.execute(
                "INSERT INTO sync_runs (started_at, status) VALUES (?, ?)", (_now(), RunStatus.RUNNING)
            )
        return cursor.lastrowid

    def finish_run(self, run_id: int, status: RunStatus, counts: SyncCounts, error: str | None = None) -> None:
        with self._connection:
            self._connection.execute(
                """
                UPDATE sync_runs
                SET finished_at = ?, status = ?, fetched = ?, new = ?, uploaded = ?, skipped = ?, failed = ?, error = ?
                WHERE id = ?
                """,
                (_now(), status, counts.fetched, counts.new, counts.uploaded,
                 counts.skipped, counts.failed, error, run_id),
            )
