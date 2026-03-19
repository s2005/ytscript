# `get_transcript.py`

Standalone transcript downloader used by the bundled Claude skill.

## Purpose

`.claude/skills/ytscript/scripts/get_transcript.py` downloads a transcript directly from YouTube, builds a markdown file, and writes it to the configured output directory.

## What It Does

- Accepts either a YouTube URL or a raw video ID
- Fetches the video title from the YouTube page
- Requests transcript data with language preference fallback
- Formats the transcript as markdown with the source video link
- Sanitizes the output filename for broad filesystem and messaging compatibility
- Writes the file into the skill output directory or `YTSCRIPT_OUTPUT_DIR`

## Example

```bash
cd .claude/skills/ytscript
uv run scripts/get_transcript.py "https://youtu.be/dQw4w9WgXcQ"
```

## Runtime

- Preferred execution: `uv run`
- If `uv` is missing:

```bash
python3 -m pip install uv
```

## Notes

- This script is independent from the repository's main `pyproject.toml`
- It is intended for ad hoc transcript retrieval before optional archiving with the sync scripts
