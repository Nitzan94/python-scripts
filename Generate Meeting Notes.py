# ABOUTME: Records audio from microphone and transcribes to text file
# ABOUTME: Generates meeting notes from voice recording using Google Speech API

import argparse
import sys
from pathlib import Path
import speech_recognition as sr


def record_meeting_notes(output_file: str = "meeting_notes.txt", duration: int = 0) -> None:
    """
    Record audio and transcribe to text file.

    Args:
        output_file: Output text filename
        duration: Recording duration in seconds (0 = until silence)
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("[INFO] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print("[INFO] Listening... (speak now)")

            if duration > 0:
                audio = recognizer.listen(source, timeout=duration)
            else:
                audio = recognizer.listen(source)

            print("[INFO] Processing audio...")

            try:
                text = recognizer.recognize_google(audio)

                if not text:
                    print("[WARN] No speech detected")
                    return

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"[OK] Meeting notes saved to {output_file}")
                print(f"[INFO] Transcribed: {text[:100]}{'...' if len(text) > 100 else ''}")

            except sr.UnknownValueError:
                print("[ERROR] Could not understand audio")
                sys.exit(1)
            except sr.RequestError as e:
                print(f"[ERROR] Speech recognition service error: {e}")
                sys.exit(1)

    except OSError as e:
        print(f"[ERROR] Microphone error: {e}")
        print("[INFO] Make sure a microphone is connected and accessible")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record meeting notes via voice transcription"
    )
    parser.add_argument(
        "-o", "--output",
        default="meeting_notes.txt",
        help="Output text filename (default: meeting_notes.txt)"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=0,
        help="Recording duration in seconds (default: 0 = until silence)"
    )

    args = parser.parse_args()
    record_meeting_notes(args.output, args.duration)


if __name__ == "__main__":
    main()