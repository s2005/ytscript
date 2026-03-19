# ytscript

Template repository for a git-backed transcript archiver.

Use this repository as a starting point for storing generated transcripts in a dated folder structure and committing them automatically.

## Using As A Template

1. Create a new repository from this one.
2. Copy `.env.example` to `.env` if you want local defaults for git identity or repo name.
3. Drop generated transcript files into `ytscript.storage/`.
4. Run the sync scripts to archive and commit them into your own repo.

## Archive Statistics

- Total transcripts: 0
- Years: 0
- Months: 0

## Usage

```bash
cp .env.example .env
python src/sync_transcript.py ytscript.storage/example.md --title "Example Video"
./scripts/force_sync.sh
python src/update_index.py
```

## Script Documentation

- [sync_transcript.py](docs/scripts/sync_transcript.md): Move a staged transcript into the archive, commit it, and try to push it
- [auto_sync.py](docs/scripts/auto_sync.md): Wrapper CLI for automation-friendly transcript syncing
- [update_index.py](docs/scripts/update_index.md): Rebuild the root README index from archived transcripts
- [get_transcript.py](docs/scripts/get_transcript.md): Download a transcript through the bundled skill script

## Layout

```text
ytscript.storage/         # Incoming transcript staging area
ytscript.storage.failed/  # Failed syncs
YYYY/MM/DD/*.md           # Archived transcripts
src/                      # Core logic
scripts/                  # Helper shell scripts
logs/                     # Runtime logs
```

## Notes

This template does not include archived transcript content, logs, secrets, or private git history.
