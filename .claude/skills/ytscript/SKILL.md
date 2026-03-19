---
name: ytscript
description: Download YouTube video transcripts and format them as readable markdown documents. Use when user wants a transcript saved to file, or when explicitly invoked ytscript skill.
argument-hint: <video-url-or-id> [--lang <langs>]
allowed-tools: Bash, Read, Write, Edit
---

# YouTube Transcript Downloader Skill (ytscript)

This skill reliably fetches full text transcripts from YouTube videos using a local Python script (via `youtube-transcript-api`).

The script is intended to be executed with `uv run`. Its Python requirement and package dependencies are embedded directly in the script header, so they do not need to be added to the repository-wide dependency files.

**Key Features:**

- **Auto-Formatting:** Saves as Markdown (`.md`) with video link.
- **Self-Contained:** Python script included with the skill for portability.
- **Embedded Requirements:** Runtime requirements are declared in the script header and resolved automatically by `uv run`.
- **Clean Filenames:** Automatically removes emojis and special characters for better file system compatibility.
- **Configurable Output:** Uses environment variable `YTSCRIPT_OUTPUT_DIR` for output location (default: `output/` subdirectory).

## Usage

Use this skill when:

- User wants a transcript saved to file.
- User specifically invokes `ytscript`.

### Command

The script is included in the skill directory at `scripts/get_transcript.py`. Run it from the skill directory with `uv run`:

```bash
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "<VIDEO_URL_OR_ID>"
```

Or set the output directory via environment variable:

```bash
export YTSCRIPT_OUTPUT_DIR="/path/to/output"
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "<VIDEO_URL_OR_ID>"
```

### Parameters

- `VIDEO_URL_OR_ID`: The full URL or video ID.
- `--lang`: Priority list of languages for transcript selection (default: `ru en`). Example: `--lang en de fr` to prefer English, then German, then French transcripts.
- Environment Variable `YTSCRIPT_OUTPUT_DIR`: Output directory path (default: `<SKILL_PATH>/ytscript/output/`)

### Runtime Requirements

- Always execute the script with `uv run scripts/get_transcript.py ...`
- Do not invoke it with plain `python` unless the embedded dependencies have been installed separately into the current environment
- The `# /// script` header in `scripts/get_transcript.py` declares the Python version and required packages

If `uv` is not installed:

```bash
python3 -m pip install uv
```

Then run:

```bash
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "<VIDEO_URL_OR_ID>"
```

### Example

User: "Save transcript for `https://youtu.be/dQw4w9WgXcQ`"
Agent Action:

```bash
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "https://youtu.be/dQw4w9WgXcQ"
```

Output:

"Successfully saved transcript to: <SKILL_PATH>/ytscript/output/Rick_Astley_-_Never_Gonna_Give_You_Up.md"

### Post-Processing (Formatting)

**IMPORTANT RULES FOR TRANSCRIPT INTEGRITY:**

**NEVER change words or alter the original meaning** of the transcript. The transcript must remain faithful to the video content.

**Section Formatting Guidelines:**

1. **Analyze content structure** - Identify main topics and sections from the transcript
2. **Add logical headings ONLY when clear sections exist** - Break text into sections with descriptive headers ONLY when the content naturally divides into distinct topics
3. **Improve formatting** - Use proper markdown syntax for lists, emphasis, and code (DO NOT add formatting that wasn't in the original)
4. **Enhance readability** - Add spacing, clear section breaks
5. **Save formatted version** - Overwrite the original file with formatted content

**When NOT to add sections:**

- If the transcript flows continuously without clear topic boundaries
- If adding sections would require paraphrasing or summarizing
- If the content is not structured in a way that allows meaningful section breaks
- If you're uncertain about where section boundaries should be

**In these cases, keep the original transcript WITHOUT any section headings.** The original text should be preserved exactly as generated, only with markdown formatting fixes (like proper list syntax, spacing) if needed.

**Golden Rule:** If you cannot add sections without changing the original text or meaning, leave the transcript as-is with NO sections.

### Filenames and Emojis

**IMPORTANT RULE:** Filenames MUST NOT contain emojis, non-ASCII characters, or ANY special symbols for maximum file system compatibility.

The `sanitize_filename()` function automatically removes:

- Emojis and non-ASCII Unicode characters
- ALL special characters (parentheses, brackets, punctuation, symbols, etc.)
- Extra whitespace (converted to underscores)

Resulting filenames contain ONLY: letters, numbers, underscores, and hyphens.

Example:

- Input: `OpenClaw Full Tutorial – How to Set Up and Use OpenClaw (ClawdBot / MoltBot)`
- Output: `OpenClaw_Full_Tutorial_How_to_Set_Up_and_Use_OpenClaw_ClawdBot_MoltBot.md`

### Delivery

After formatting and validation, deliver the transcript to the user:

1. **Sync to GitHub (optional)** - If using a repository system like ytfav, archive the transcript
2. **Send the file** - Use appropriate delivery method for your platform
3. **Write summary** - Provide a concise summary of the video content with key points
   - List main topics/reasons covered
   - Include conclusion/takeaway
   - Reference original video URL and transcript file location

**Example message format:**

```text
# Transcript: [Video Title]

## Key Points

**Point 1:** [Brief description]

**Point 2:** [Brief description]

**Conclusion:** [Main takeaway]

**Source:** [YouTube URL]
**Full transcript:** [File path to transcript]
```

### Git Archiving (ytscript-public Template)

**IMPORTANT:** This template uses a two-stage workflow for transcript archiving.

**Workflow:**

1. **Download & Edit** (gitignored working directory):
   - Transcript downloads to `.claude/skills/ytscript/output/` (gitignored)
   - AI formats and validates in place

2. **Archive & Commit** (final location):
   - Move formatted transcript to dated directory structure
   - Commit directly to git

**Complete workflow:**

```bash
# 1. Download (script outputs to .claude/skills/ytscript/output/)
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# 2. Format and validate in place (AI adds sections, fixes linting)
# File: .claude/skills/ytscript/output/Video_Title.md

# 3. Move to archive directory (creates YYYY/MM/DD/ structure)
TRANSCRIPT_FILE=".claude/skills/ytscript/output/Video_Title.md"
ARCHIVE_DATE=$(date +%Y/%m/%d)
mkdir -p "$ARCHIVE_DATE"
mv "$TRANSCRIPT_FILE" "$ARCHIVE_DATE/Video_Title.md"

# 4. Commit to git
git add "$ARCHIVE_DATE/Video_Title.md"
git commit -m "Add transcript: Video Title

Source: https://www.youtube.com/watch?v=VIDEO_ID"
```

**Note:** The source file is removed when moved to the archive directory.

#### Windows (Git Bash / MSYS2)

The bash commands above work in Git Bash on Windows. If you encounter issues, use this alternative:

```bash
# 1. Download
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# 2. Format and validate in place

# 3. Move to archive directory
TRANSCRIPT_FILE=".claude/skills/ytscript/output/Video_Title.md"
ARCHIVE_DATE="$(date +%Y/%m/%d)"
mkdir -p "$ARCHIVE_DATE"
mv "$TRANSCRIPT_FILE" "$ARCHIVE_DATE/Video_Title.md"

# 4. Commit to git (use -m and then open editor for multi-line message)
git add "$ARCHIVE_DATE/Video_Title.md"
git commit -m "Add transcript: Video Title" -m "Source: https://www.youtube.com/watch?v=VIDEO_ID"
```

### Optional GitHub Integration

If you want to automatically archive transcripts to a GitHub repository:

**Workflow:**

1. Set `YTSCRIPT_OUTPUT_DIR` environment variable to your archive directory
2. ytscript downloads transcript to that directory
3. AI formats transcript with meaningful filename
4. Use your synchronization tool (git, ytfav, etc.) to commit and push

**Example with environment variable:**

```bash
export YTSCRIPT_OUTPUT_DIR="/path/to/your/archive/storage"
cd <SKILL_PATH>/ytscript
uv run scripts/get_transcript.py "https://youtube.com/watch?v=abc123"
# Transcript saved to: /path/to/your/archive/storage/VideoTitle.md
```

**Note:** The skill itself does not include archiving logic - that's project-specific. The transcript is saved to the location specified by `YTSCRIPT_OUTPUT_DIR` or the default `output/` subdirectory.

### Markdown Linter Compliance

**CRITICAL:** Always format transcripts to avoid markdownlint errors. Follow these rules:

| Rule | Description | Fix |
| ---- | ----------- | --- |
| **MD013** | Line length | IGNORED - transcripts may have long lines |
| **MD032** | Lists must be surrounded by blank lines | Add blank line before/after lists |
| **MD036** | Don't use emphasis (asterisks or underscores) as headings | Use proper #, ##, or ### headings |
| **MD060** | Table separators need spaces around pipes | Use proper spacing: pipe-space-dash-space-pipe |

#### Common Mistakes to Avoid

**❌ WRONG (MD032 - Missing blank lines):**

```markdown
Here's a list:
- Item 1
- Item 2

Another paragraph.
```

**✅ CORRECT:**

```markdown
Here's a list:

- Item 1
- Item 2

Another paragraph.
```

**❌ WRONG (MD036 - Emphasis as heading):**

```markdown
*This is a heading*
```

**✅ CORRECT:**

```markdown
## This is a heading
```

**❌ WRONG (MD060 - No spaces in table separator):**

```markdown
| Column |
|--------|
| value  |
```

**✅ CORRECT:**

```markdown
| Column |
| ------ |
| value  |
```

#### Verification

After formatting, check for errors:

```bash
markdownlint-cli2 "/path/to/transcript.md"
```

Fix all reported errors before delivering the transcript.
