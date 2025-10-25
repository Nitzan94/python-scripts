# ABOUTME: Downloads YouTube video transcripts and subtitles
# ABOUTME: Supports multiple languages, timestamp options, and format exports

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter, JSONFormatter
import re


def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL or video ID

    Returns:
        Video ID string
    """
    # Handle various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
        r'youtube\.com\/embed\/([^&\n?]*)',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    print(f"[ERROR] Could not extract video ID from: {url}")
    sys.exit(1)


def get_transcript(
    video_id: str,
    languages: List[str] = None
) -> List[dict]:
    """
    Get transcript for video.

    Args:
        video_id: YouTube video ID
        languages: List of language codes (e.g., ['en', 'es'])

    Returns:
        List of transcript segments
    """
    try:
        if languages:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=languages
            )
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

        return transcript

    except Exception as e:
        print(f"[ERROR] Failed to get transcript: {e}")
        print("[INFO] Video may not have captions or may be unavailable")
        sys.exit(1)


def list_available_transcripts(video_id: str) -> None:
    """List all available transcript languages."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        print("\n[INFO] Available transcripts:")
        print("-" * 50)

        for transcript in transcript_list:
            lang_code = transcript.language_code
            lang_name = transcript.language
            is_generated = transcript.is_generated
            status = "(auto-generated)" if is_generated else "(manual)"
            print(f"  {lang_code}: {lang_name} {status}")

    except Exception as e:
        print(f"[ERROR] Failed to list transcripts: {e}")
        sys.exit(1)


def format_transcript(
    transcript: List[dict],
    format_type: str = "text",
    include_timestamps: bool = False
) -> str:
    """
    Format transcript to specified format.

    Args:
        transcript: Transcript data
        format_type: Output format (text, srt, json)
        include_timestamps: Include timestamps in text format

    Returns:
        Formatted transcript string
    """
    if format_type == "srt":
        formatter = SRTFormatter()
        return formatter.format_transcript(transcript)
    elif format_type == "json":
        formatter = JSONFormatter()
        return formatter.format_transcript(transcript)
    else:  # text
        if include_timestamps:
            lines = []
            for entry in transcript:
                timestamp = f"[{int(entry['start'])}s]"
                text = entry['text']
                lines.append(f"{timestamp} {text}")
            return "\n".join(lines)
        else:
            formatter = TextFormatter()
            return formatter.format_transcript(transcript)


def download_transcript(
    url: str,
    output_file: str = None,
    format_type: str = "text",
    languages: List[str] = None,
    include_timestamps: bool = False
) -> None:
    """
    Download and save transcript.

    Args:
        url: YouTube URL or video ID
        output_file: Output filename
        format_type: Output format (text, srt, json)
        languages: Language codes to try
        include_timestamps: Include timestamps in text format
    """
    video_id = extract_video_id(url)

    print(f"[INFO] Downloading transcript for video: {video_id}")

    transcript = get_transcript(video_id, languages)

    print(f"[INFO] Found {len(transcript)} transcript segments")

    formatted = format_transcript(transcript, format_type, include_timestamps)

    # Determine output filename
    if not output_file:
        ext = {"text": "txt", "srt": "srt", "json": "json"}[format_type]
        output_file = f"transcript_{video_id}.{ext}"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted)

    print(f"[OK] Transcript saved to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download YouTube video transcripts"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Download command
    dl_parser = subparsers.add_parser("download", help="Download transcript")
    dl_parser.add_argument(
        "url",
        help="YouTube URL or video ID"
    )
    dl_parser.add_argument(
        "-o", "--output",
        help="Output filename"
    )
    dl_parser.add_argument(
        "-f", "--format",
        choices=["text", "srt", "json"],
        default="text",
        help="Output format (default: text)"
    )
    dl_parser.add_argument(
        "-l", "--languages",
        nargs="+",
        help="Language codes to try (e.g., en es fr)"
    )
    dl_parser.add_argument(
        "-t", "--timestamps",
        action="store_true",
        help="Include timestamps (text format only)"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available transcripts")
    list_parser.add_argument(
        "url",
        help="YouTube URL or video ID"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "download":
        download_transcript(
            args.url,
            args.output,
            args.format,
            args.languages,
            args.timestamps
        )
    elif args.command == "list":
        video_id = extract_video_id(args.url)
        list_available_transcripts(video_id)


if __name__ == "__main__":
    main()
