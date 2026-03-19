#!/usr/bin/env python3
"""
Generate a README index for archived transcripts.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = PROJECT_ROOT
README_PATH = PROJECT_ROOT / "README.md"


def collect_transcripts() -> dict[str, dict[str, list[dict[str, object]]]]:
    """Collect archived transcripts grouped by year and month."""
    archive: dict[str, dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))

    for year_dir in sorted(ARCHIVE_DIR.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir() or not month_dir.name.isdigit():
                continue

            for day_dir in sorted(month_dir.iterdir()):
                if not day_dir.is_dir() or not day_dir.name.isdigit():
                    continue

                for md_file in sorted(day_dir.glob("*.md")):
                    filename = md_file.stem
                    time_part, title = filename.split("_", 1) if "_" in filename else ("0000", filename)

                    try:
                        timestamp = datetime(
                            int(year_dir.name),
                            int(month_dir.name),
                            int(day_dir.name),
                            int(time_part[:2]),
                            int(time_part[2:4]),
                        )
                    except ValueError:
                        timestamp = datetime(int(year_dir.name), int(month_dir.name), int(day_dir.name))

                    archive[year_dir.name][month_dir.name].append(
                        {
                            "day": day_dir.name,
                            "time": time_part,
                            "title": title,
                            "path": str(md_file.relative_to(PROJECT_ROOT)),
                            "timestamp": timestamp,
                        }
                    )

    for year in archive.values():
        for transcripts in year.values():
            transcripts.sort(key=lambda item: item["timestamp"])

    return {year: dict(months) for year, months in archive.items()}


def count_transcripts(archive: dict[str, dict[str, list[dict[str, object]]]]) -> dict[str, int]:
    """Return archive summary counts."""
    total = 0
    years = len(archive)
    months = 0

    for months_data in archive.values():
        months += len(months_data)
        for transcripts in months_data.values():
            total += len(transcripts)

    return {"total": total, "years": years, "months": months}


def get_recent_transcripts(
    archive: dict[str, dict[str, list[dict[str, object]]]],
    limit: int = 10,
) -> list[dict[str, object]]:
    """Return the most recent transcripts."""
    transcripts: list[dict[str, object]] = []
    for months_data in archive.values():
        for entries in months_data.values():
            transcripts.extend(entries)
    transcripts.sort(key=lambda item: item["timestamp"], reverse=True)
    return transcripts[:limit]


def generate_index() -> str:
    """Build a public README with archive stats and links."""
    archive = collect_transcripts()
    stats = count_transcripts(archive)
    recent = get_recent_transcripts(archive)

    lines = [
        "# ytscript-public",
        "",
        "Template repository for a git-backed transcript archiver.",
        "",
        "Use this repository as a starting point for storing generated transcripts in a dated folder structure and committing them automatically.",
        "",
        "## Using As A Template",
        "",
        "1. Create a new repository from this one.",
        "2. Copy `.env.example` to `.env` if you want local defaults for git identity or repo name.",
        "3. Drop generated transcript files into `ytscript.storage/`.",
        "4. Run the sync scripts to archive and commit them into your own repo.",
        "",
        "## Archive Statistics",
        "",
        f"- Total transcripts: {stats['total']}",
        f"- Years: {stats['years']}",
        f"- Months: {stats['months']}",
        "",
    ]

    if recent:
        lines.extend(
            [
                "## Recent Transcripts",
                "",
                "| Date | Time | Title | Link |",
                "| ---- | ---- | ----- | ---- |",
            ]
        )
        for transcript in recent:
            lines.append(
                f"| {transcript['day']} | {str(transcript['time'])[:2]}:{str(transcript['time'])[2:]} | "
                f"{str(transcript['title']).replace('_', ' ')} | "
                f"[View]({transcript['path']}) |"
            )
        lines.append("")

    if archive:
        lines.extend(["## Full Index", ""])
        for year in sorted(archive.keys(), reverse=True):
            lines.extend([f"### {year}", ""])
            for month in sorted(archive[year].keys(), reverse=True):
                entries = archive[year][month]
                month_name = datetime(int(year), int(month), 1).strftime("%B")
                lines.extend(
                    [
                        f"#### {month_name} ({len(entries)} transcripts)",
                        "",
                        "| Day | Time | Title | Link |",
                        "| --- | ---- | ----- | ---- |",
                    ]
                )
                for transcript in entries:
                    lines.append(
                        f"| {transcript['day']} | {str(transcript['time'])[:2]}:{str(transcript['time'])[2:]} | "
                        f"{str(transcript['title']).replace('_', ' ')} | "
                        f"[View]({transcript['path']}) |"
                    )
                lines.append("")

    lines.extend(
        [
            "## Usage",
            "",
            "```bash",
            "cp .env.example .env",
            "python src/sync_transcript.py ytscript.storage/example.md --title \"Example Video\"",
            "./scripts/force_sync.sh",
            "python src/update_index.py",
            "```",
            "",
            "## Script Documentation",
            "",
            "- [sync_transcript.py](docs/scripts/sync_transcript.md): Move a staged transcript into the archive, commit it, and try to push it",
            "- [auto_sync.py](docs/scripts/auto_sync.md): Wrapper CLI for automation-friendly transcript syncing",
            "- [update_index.py](docs/scripts/update_index.md): Rebuild the root README index from archived transcripts",
            "- [get_transcript.py](docs/scripts/get_transcript.md): Download a transcript through the bundled skill script",
            "",
            "## Layout",
            "",
            "```text",
            "ytscript.storage/         # Incoming transcript staging area",
            "ytscript.storage.failed/  # Failed syncs",
            "YYYY/MM/DD/*.md           # Archived transcripts",
            "src/                      # Core logic",
            "scripts/                  # Helper shell scripts",
            "logs/                     # Runtime logs",
            "```",
            "",
            "## Notes",
            "",
            "This template does not include archived transcript content, logs, secrets, or private git history.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    """Generate the README file in place."""
    README_PATH.write_text(generate_index(), encoding="utf-8")
    total = count_transcripts(collect_transcripts())["total"]
    print(f"Updated {README_PATH} with {total} transcript(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
