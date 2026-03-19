# `update_index.py`

README index generator for the transcript archive.

## Purpose

`src/update_index.py` scans archived transcript files and rebuilds the repository `README.md` with current archive statistics and index tables.

## What It Does

- Walks the archive tree using the `YYYY/MM/DD/*.md` layout
- Collects transcript metadata from filenames and paths
- Counts total transcripts, years, and months
- Builds a recent transcripts table
- Builds a full year and month index
- Rewrites the root `README.md` in place

## Example

```bash
python src/update_index.py
```

## Notes

- This script overwrites the root `README.md`
- Any persistent README content should also be reflected in the `generate_index()` template
- The script expects archive files to use the repository naming format
