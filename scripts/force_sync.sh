#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STORAGE_DIR="$PROJECT_ROOT/ytscript.storage"
FAILED_DIR="$PROJECT_ROOT/ytscript.storage.failed"
SYNC_SCRIPT="$PROJECT_ROOT/src/sync_transcript.py"

echo "======================================"
echo "ytscript-public batch synchronization"
echo "======================================"
echo ""

if [ ! -d "$STORAGE_DIR" ]; then
    echo "Storage directory not found: $STORAGE_DIR"
    mkdir -p "$STORAGE_DIR"
    echo "Created storage directory. No files to sync."
    exit 0
fi

FILES=()
while IFS= read -r -d '' file; do
    FILES+=("$file")
done < <(find "$STORAGE_DIR" -maxdepth 1 -name "*.md" -print0)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "No transcript files found in $STORAGE_DIR"
    exit 0
fi

SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL=${#FILES[@]}

echo "Found ${TOTAL} transcript file(s)"
echo ""

for file in "${FILES[@]}"; do
    filename="$(basename "$file")"
    basename="${filename%.md}"

    if [[ $basename =~ ^[0-9]{4}_(.+)$ ]]; then
        title="${BASH_REMATCH[1]}"
    else
        title="$basename"
    fi

    echo "[$((SUCCESS_COUNT + FAIL_COUNT + 1))/$TOTAL] Processing: $filename"

    if python "$SYNC_SCRIPT" "$file" --title "$title"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "  OK"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "  FAILED"
    fi

    echo ""
done

echo "Summary: total=$TOTAL success=$SUCCESS_COUNT failed=$FAIL_COUNT"

if [ -d "$FAILED_DIR" ] && [ "$(ls -A "$FAILED_DIR" 2>/dev/null)" ]; then
    echo "Failed files were moved to $FAILED_DIR"
fi

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
