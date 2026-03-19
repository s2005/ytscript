# ytscript

Template repository for a git-backed transcript archiver using the ytscript skill.

Download YouTube video transcripts as formatted markdown documents and archive them in a dated folder structure.

## Using As A Template

1. Create a new repository from this one.
2. Copy `.env.example` to `.env` if you want local defaults for git identity or repo name.
3. Install `uv` for running the transcript script: `python3 -m pip install uv`
4. Use the ytscript skill to download transcripts

## Archive Statistics

- Total transcripts: 0
- Years: 0
- Months: 0

## Usage

The ytscript skill downloads transcripts to `.claude/skills/ytscript/output/` (gitignored working directory).

### Download Transcript

```bash
cd .claude/skills/ytscript
uv run scripts/get_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
```

Optional: Set custom output directory via environment variable:

```bash
export YTSCRIPT_OUTPUT_DIR="/path/to/output"
uv run scripts/get_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
```

### Archive and Commit

After AI formats the transcript in place, move it to the archive:

```bash
# Move to dated directory structure
TRANSCRIPT_FILE=".claude/skills/ytscript/output/Video_Title.md"
ARCHIVE_DATE="$(date +%Y/%m/%d)"
mkdir -p "$ARCHIVE_DATE"
mv "$TRANSCRIPT_FILE" "$ARCHIVE_DATE/Video_Title.md"

# Commit to git
git add "$ARCHIVE_DATE/Video_Title.md"
git commit -m "Add transcript: Video Title" -m "Source: https://www.youtube.com/watch?v=VIDEO_ID"
```

## Script Documentation

- [sync_transcript.py](docs/scripts/sync_transcript.md): Move a staged transcript into the archive, commit it, and try to push it
- [auto_sync.py](docs/scripts/auto_sync.md): Wrapper CLI for automation-friendly transcript syncing
- [update_index.py](docs/scripts/update_index.md): Rebuild the root README index from archived transcripts
- [get_transcript.py](docs/scripts/get_transcript.md): Download a transcript through the bundled skill script

## Layout

```text
.claude/skills/ytscript/output/  # Downloaded transcripts (gitignored)
YYYY/MM/DD/*.md                  # Archived transcripts
src/                             # Core logic
scripts/                         # Helper shell scripts
docs/                            # Documentation
```

## Notes

- This template uses a two-stage workflow: download/edit in gitignored directory, then archive and commit
- Filenames are automatically sanitized (emojis and special characters removed)
- Transcripts are formatted as markdown with video link included
- The skill itself does not include archiving logic - that's project-specific
