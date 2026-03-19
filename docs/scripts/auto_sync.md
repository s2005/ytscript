# `auto_sync.py`

Wrapper entry point for automation that already has a transcript file and video metadata.

## Purpose

`src/auto_sync.py` provides a simpler interface around `sync_transcript.py` for external tools, agents, or workflows that want a machine-friendly success or failure result.

## What It Does

- Resolves transcript paths relative to `ytscript.storage/`
- Calls the core `sync_transcript()` function
- Returns a structured result object with:
  - success status
  - status message
  - expected archive path on success
  - error text on failure

## Inputs

- Positional argument: transcript file path
- `--title`: required video title
- `--url`: optional source URL
- `--date`: optional timestamp in `YYYY-MM-DD HH:MM:SS` format

## Example

```bash
python src/auto_sync.py ytscript.storage/example.md --title "Example Video"
```

## Notes

- This script does not contain separate archive logic
- It delegates the actual move, commit, and optional push to `sync_transcript.py`
- Useful when another system needs a predictable CLI result
