# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "youtube-transcript-api>=0.6.0",
#     "requests",
#     "beautifulsoup4",
# ]
# ///

import argparse
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(value):
    """
    Extracts the video ID from a YouTube URL or returns the value if it's already an ID.
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
            
    if len(value) == 11:
        return value
        
    return value

def get_video_title(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find("meta", property="og:title")
            if title_tag:
                return title_tag["content"]
            # Fallback to title element
            return soup.title.string.replace(" - YouTube", "")
    except Exception as e:
        print(f"Warning: Could not fetch title: {e}", file=sys.stderr)
    return f"Video_{video_id}"

def sanitize_filename(name):
    """
    Sanitize filename by removing:
    - Emojis and non-ASCII characters
    - ALL special characters (including parentheses, brackets, punctuation)
    - Extra whitespace
    
    Keeps only: letters, numbers, hyphens, underscores
    """
    # Remove emojis and non-ASCII characters
    name = re.sub(r'[^\x00-\x7F]+', '', name)
    # Replace multiple spaces and other whitespace with single space
    name = re.sub(r'\s+', ' ', name)
    # Remove leading/trailing whitespace
    name = name.strip()
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove ALL special characters except letters, numbers, hyphens, underscores
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    # Remove consecutive underscores/hyphens
    name = re.sub(r'[-_]{2,}', '_', name)
    return name

def main():
    parser = argparse.ArgumentParser(description="Download YouTube video transcript to Markdown.")
    parser.add_argument("video", help="YouTube Video URL or ID")
    parser.add_argument("--lang", nargs="+", default=["ru", "en"], help="Priority list of languages (default: ru en)")
    
    args = parser.parse_args()
    
    video_id = extract_video_id(args.video)
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print(f"Fetching data for Video ID: {video_id}...")
    
    # Fetch title
    title = get_video_title(video_id)
    print(f"Title: {title}")
    
    try:
        # Fetch transcript
        if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        else:
            # Fallback for instance-based API (if installed version differs)
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
        
        # Try to find transcript (manual > generated)
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(args.lang)
        except:
            try:
                transcript = transcript_list.find_generated_transcript(args.lang)
            except:
                # If neither, just take the first available if possible or fail
                # But find_generated should catch it if it exists in that lang.
                # If specifically requested langs are missing, we might want to fallback to any?
                # For now, let's stick to the requested logic or fallback to first available.
                try:
                    transcript = transcript_list.find_transcript(args.lang)
                except:
                     # Fallback to the first one available if specific lang not found
                    transcript = next(iter(transcript_list))
                    print(f"Requested languages {args.lang} not found. Using {transcript.language_code}.")

        print(f"Found transcript: {transcript.language} ({'Auto-generated' if transcript.is_generated else 'Manual'})")
        
        data = transcript.fetch()
        
        # Format as simple text blocks for MD
        # We can use TextFormatter for the body, but let's keep it simple.
        formatter = TextFormatter()
        text_content = formatter.format_transcript(data)
        
        # Construct Markdown
        md_content = f"# {title}\n\n"
        md_content += f"**Original Video:** [{video_url}]({video_url})\n\n"
        md_content += "## Transcript\n\n"
        md_content += text_content
        
        # Save
        skill_root = Path(__file__).resolve().parent.parent
        output_dir = os.getenv("YTSCRIPT_OUTPUT_DIR", str(skill_root / "output"))
        os.makedirs(output_dir, exist_ok=True)
        
        safe_title = sanitize_filename(title)
        filename = os.path.join(output_dir, f"{safe_title}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"Successfully saved transcript to: {filename}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
