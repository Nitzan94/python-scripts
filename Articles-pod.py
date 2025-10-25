# ABOUTME: Converts web articles to MP3 audio files using text-to-speech
# ABOUTME: Scrapes article text and generates audio podcast version

import argparse
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pyttsx3


def article_to_audio(url: str, output_file: str = "article.mp3") -> None:
    """
    Convert web article to audio file.

    Args:
        url: Article URL to convert
        output_file: Output MP3 filename
    """
    try:
        print(f"[INFO] Fetching article from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")

        if not paragraphs:
            print("[ERROR] No paragraphs found in article")
            sys.exit(1)

        text = " ".join([p.text.strip() for p in paragraphs])

        if not text:
            print("[ERROR] No text extracted from article")
            sys.exit(1)

        print(f"[INFO] Extracted {len(text)} characters")
        print("[INFO] Generating audio file...")

        engine = pyttsx3.init()
        engine.save_to_file(text, output_file)
        engine.runAndWait()

        if Path(output_file).exists():
            print(f"[OK] Audio saved to {output_file}")
        else:
            print("[ERROR] Failed to create audio file")
            sys.exit(1)

    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch article: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert web articles to audio podcasts"
    )
    parser.add_argument("url", help="Article URL to convert")
    parser.add_argument(
        "-o", "--output",
        default="article.mp3",
        help="Output MP3 filename (default: article.mp3)"
    )

    args = parser.parse_args()
    article_to_audio(args.url, args.output)


if __name__ == "__main__":
    main()