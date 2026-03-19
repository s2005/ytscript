#!/usr/bin/env python3
"""
Core synchronization logic for archived YouTube transcripts.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import git
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

STORAGE_DIR = PROJECT_ROOT / "ytscript.storage"
FAILED_DIR = PROJECT_ROOT / "ytscript.storage.failed"
ARCHIVE_DIR = PROJECT_ROOT
LOG_FILE = PROJECT_ROOT / "logs" / "sync.log"

GIT_USER = os.environ.get("GIT_USER", "")
GIT_EMAIL = os.environ.get("GIT_EMAIL", "")

MAX_RETRIES = 3
RETRY_DELAY = 5


def setup_logging() -> logging.Logger:
    """Configure logging to file and stdout without duplicating handlers."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("ytscript_public")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()


def get_date_path(target_date: datetime | None = None) -> Path:
    """Return the archive directory for a given date."""
    target_date = target_date or datetime.now()
    return ARCHIVE_DIR / target_date.strftime("%Y") / target_date.strftime("%m") / target_date.strftime("%d")


def format_filename(video_title: str, target_time: datetime | None = None) -> str:
    """Return a sanitized archive filename."""
    target_time = target_time or datetime.now()
    time_str = target_time.strftime("%H%M")
    sanitized_title = video_title.replace(" ", "_")
    sanitized_title = "".join(char for char in sanitized_title if char.isalnum() or char in "_-.")
    sanitized_title = sanitized_title.strip("._") or "untitled"
    return f"{time_str}_{sanitized_title}.md"


def git_with_retry(operation_name: str, operation_func: Callable[[], None]) -> tuple[bool, Exception | None]:
    """Execute a git operation with retries."""
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            operation_func()
            return True, None
        except Exception as exc:  # pragma: no cover - direct git errors are environment-dependent
            last_error = exc
            logger.warning("%s failed (%s/%s): %s", operation_name, attempt, MAX_RETRIES, exc)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    logger.error("%s failed after %s attempts", operation_name, MAX_RETRIES)
    return False, last_error


def resolve_transcript_path(transcript_file: str | Path) -> Path:
    """Resolve a transcript path against the staging directory when needed."""
    transcript_path = Path(transcript_file)
    if transcript_path.is_absolute():
        return transcript_path

    if str(transcript_path).startswith("ytscript.storage/"):
        return PROJECT_ROOT / transcript_path

    return STORAGE_DIR / transcript_path


def move_to_failed(file_path: Path, original_name: str) -> None:
    """Move a failed transcript to the failed staging directory."""
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    failed_name = f"{datetime.now():%Y%m%d_%H%M%S}_{original_name}"
    failed_path = FAILED_DIR / failed_name

    try:
        shutil.move(str(file_path), str(failed_path))
        logger.warning("Moved failed file to %s", failed_path.relative_to(PROJECT_ROOT))
    except Exception as exc:  # pragma: no cover - environment-dependent filesystem failures
        logger.error("Failed to move file to failed directory: %s", exc)


def sync_transcript(
    transcript_path: Path | str,
    video_title: str,
    video_url: str | None = None,
    target_datetime: datetime | None = None,
) -> bool:
    """Move a transcript into the archive and commit it locally."""
    start_time = time.time()
    transcript_path = resolve_transcript_path(transcript_path)

    if not transcript_path.exists():
        logger.error("Transcript file not found: %s", transcript_path)
        return False

    target_datetime = target_datetime or datetime.now()
    date_path = get_date_path(target_datetime)
    date_path.mkdir(parents=True, exist_ok=True)

    filename = format_filename(video_title, target_datetime)
    dest_path = date_path / filename

    counter = 1
    while dest_path.exists():
        dest_path = date_path / f"{Path(filename).stem}_{counter}.md"
        counter += 1

    try:
        shutil.move(str(transcript_path), str(dest_path))
        logger.info("Moved transcript to %s", dest_path.relative_to(PROJECT_ROOT))

        repo = git.Repo(PROJECT_ROOT)
        if GIT_USER and GIT_EMAIL:
            with repo.config_writer() as config:
                config.set_value("user", "name", GIT_USER)
                config.set_value("user", "email", GIT_EMAIL)

        relative_path = str(dest_path.relative_to(PROJECT_ROOT))
        success, error = git_with_retry("git add", lambda: repo.index.add([relative_path]))
        if not success:
            logger.error("Failed to stage file: %s", error)
            move_to_failed(dest_path, transcript_path.name)
            return False

        commit_lines = [f"Add transcript: {dest_path.stem}"]
        if video_url:
            commit_lines.extend(["", f"Source: {video_url}"])
        commit_lines.extend(["", f"Date: {target_datetime:%Y-%m-%d}"])
        success, error = git_with_retry("git commit", lambda: repo.index.commit("\n".join(commit_lines)))
        if not success:
            logger.error("Failed to commit file: %s", error)
            move_to_failed(dest_path, transcript_path.name)
            return False

        try:
            origin = repo.remote(name="origin")
        except ValueError:
            origin = None

        if origin is not None:
            success, error = git_with_retry("git push", lambda: origin.push())
            if not success:
                logger.warning("Push failed; transcript is committed locally: %s", error)

        logger.info("Sync completed in %.1fs", time.time() - start_time)
        return True
    except Exception as exc:  # pragma: no cover - environment-dependent filesystem/git failures
        logger.error("Unexpected error during sync: %s", exc, exc_info=True)
        if dest_path.exists():
            move_to_failed(dest_path, transcript_path.name)
        elif transcript_path.exists():
            move_to_failed(transcript_path, transcript_path.name)
        return False


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync a transcript into the local archive")
    parser.add_argument("file", help="Path to transcript file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--url", help="YouTube URL")
    parser.add_argument("--date", help="Target date in 'YYYY-MM-DD HH:MM:SS' format")
    args = parser.parse_args()

    target_datetime = None
    if args.date:
        target_datetime = datetime.strptime(args.date, "%Y-%m-%d %H:%M:%S")

    return 0 if sync_transcript(args.file, args.title, args.url, target_datetime) else 1


if __name__ == "__main__":
    raise SystemExit(main())
