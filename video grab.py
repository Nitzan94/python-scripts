# ABOUTME: Downloads videos from YouTube and other platforms using yt-dlp
# ABOUTME: Supports quality selection, audio extraction, and playlist downloads

import argparse
import sys
from pathlib import Path
from typing import Optional
import yt_dlp


def download_video(
    url: str,
    output_dir: str = ".",
    quality: str = "best",
    audio_only: bool = False,
    playlist: bool = False
) -> None:
    """
    Download video from URL.

    Args:
        url: Video or playlist URL
        output_dir: Output directory
        quality: Video quality (best, 1080p, 720p, 480p)
        audio_only: Extract audio only
        playlist: Download entire playlist
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Format selection based on quality
        if audio_only:
            format_str = "bestaudio/best"
            ext = "mp3"
        elif quality == "best":
            format_str = "bestvideo+bestaudio/best"
            ext = "mp4"
        else:
            height = quality.replace("p", "")
            format_str = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
            ext = "mp4"

        opts = {
            "format": format_str,
            "outtmpl": str(output_path / "%(uploader)s" / "%(title)s.%(ext)s"),
            "merge_output_format": ext,
            "noplaylist": not playlist,
            "quiet": False,
            "no_warnings": False,
            "ignoreerrors": False,
        }

        if audio_only:
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        print(f"[INFO] Downloading from: {url}")
        print(f"[INFO] Quality: {quality}, Audio only: {audio_only}, Playlist: {playlist}")

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if "entries" in info and playlist:
                print(f"[INFO] Found playlist with {len(info['entries'])} videos")

            ydl.download([url])

        print("[OK] Download completed")

    except yt_dlp.utils.DownloadError as e:
        print(f"[ERROR] Download failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download videos from YouTube and other platforms"
    )
    parser.add_argument(
        "url",
        help="Video or playlist URL"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Output directory (default: current dir)"
    )
    parser.add_argument(
        "-q", "--quality",
        choices=["best", "1080p", "720p", "480p"],
        default="best",
        help="Video quality (default: best)"
    )
    parser.add_argument(
        "-a", "--audio-only",
        action="store_true",
        help="Extract audio only (MP3)"
    )
    parser.add_argument(
        "-p", "--playlist",
        action="store_true",
        help="Download entire playlist"
    )

    args = parser.parse_args()
    download_video(
        args.url,
        args.output_dir,
        args.quality,
        args.audio_only,
        args.playlist
    )


if __name__ == "__main__":
    main()