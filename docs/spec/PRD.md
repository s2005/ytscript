# ytscript-public Template PRD

## Goal

Create a clean public template repository for transcript archiving without exposing private data, history, or operational residue.

## Scope

Included:

- transcript staging and archive sync logic
- batch sync tooling
- README index generation
- basic repository bootstrap script

Excluded:

- private git history
- archived transcript content
- downloads, logs, and temporary files
- `.env` files and any credentials

## Template Requirements

1. Accept transcript files from `ytscript.storage/`.
2. Move archived transcripts into `YYYY/MM/DD/HHmm_Title.md`.
3. Commit new transcripts into the local git repository.
4. Attempt a push when an `origin` remote is configured.
5. Move failed items into `ytscript.storage.failed/`.
6. Rebuild `README.md` from archive contents.

## Usage Model

Users are expected to create their own repository from this template, configure local git identity if needed, and publish to their own GitHub remote.
