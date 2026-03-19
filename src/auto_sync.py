#!/usr/bin/env python3
"""
Wrapper entry point for external transcript automation.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_transcript import PROJECT_ROOT, get_date_path, format_filename, logger, sync_transcript


STORAGE_DIR = PROJECT_ROOT / "ytscript.storage"


def auto_sync(
    transcript_file: str,
    video_title: str,
    video_url: str = "",
    target_datetime: datetime | None = None,
) -> dict[str, str | bool | None]:
    """Sync a transcript and return a machine-friendly result object."""
    transcript_path = Path(transcript_file)
    if not transcript_path.is_absolute():
        if str(transcript_path).startswith("ytscript.storage/"):
            transcript_path = PROJECT_ROOT / transcript_path
        else:
            transcript_path = STORAGE_DIR / transcript_path

    logger.info("Auto-sync started for %s", transcript_path.name)

    success = sync_transcript(transcript_path, video_title, video_url, target_datetime)
    if success:
        return {
            "success": True,
            "message": f"Successfully synced '{video_title}'",
            "archive_path": get_archive_path(video_title, target_datetime),
            "error": None,
        }

    return {
        "success": False,
        "message": f"Failed to sync '{video_title}'",
        "archive_path": None,
        "error": "Check logs/sync.log for details",
    }


def get_archive_path(video_title: str, target_datetime: datetime | None = None) -> str:
    """Return the expected archive path for a transcript."""
    target_datetime = target_datetime or datetime.now()
    date_path = get_date_path(target_datetime)
    filename = format_filename(video_title, target_datetime)
    return str((date_path / filename).relative_to(PROJECT_ROOT))


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-sync wrapper for transcript generation workflows")
    parser.add_argument("file", help="Path to transcript file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--url", default="", help="YouTube URL")
    parser.add_argument("--date", help="Target date in 'YYYY-MM-DD HH:MM:SS' format")
    args = parser.parse_args()

    target_datetime = None
    if args.date:
        target_datetime = datetime.strptime(args.date, "%Y-%m-%d %H:%M:%S")

    result = auto_sync(args.file, args.title, args.url, target_datetime)
    print(result)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
