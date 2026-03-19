# `sync_transcript.py`

Core archive ingestion script for transcript files.

## Purpose

`src/sync_transcript.py` moves a transcript from the staging area into the dated archive structure, creates a git commit for the new file, and attempts to push the commit to `origin` when a remote is configured.

## What It Does

- Resolves the input transcript path relative to `ytscript.storage/` when needed
- Creates the target archive directory in `YYYY/MM/DD/` format
- Builds a sanitized filename from the video title and target time
- Moves the transcript into the archive
- Stages and commits the archived file with GitPython
- Attempts a `git push` if the repository has an `origin` remote
- Moves failed files into `ytscript.storage.failed/`
- Writes runtime logs to `logs/sync.log`

## Inputs

- Positional argument: transcript file path
- `--title`: required video title used for archive naming
- `--url`: optional source URL included in the commit message
- `--date`: optional timestamp in `YYYY-MM-DD HH:MM:SS` format

## Example

```bash
python src/sync_transcript.py ytscript.storage/example.md --title "Example Video"
```

## Notes

- Requires the repository to already be initialized as a git repository
- Uses local git identity from environment variables when available
- Push failures do not remove the local commit
