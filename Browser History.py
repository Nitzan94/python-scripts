# ABOUTME: Extracts Chrome browsing history to markdown journal
# ABOUTME: Generates daily journal from browser activity

import argparse
import datetime
import os
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple


def get_chrome_history(db_path: str, limit: int = 50) -> List[Tuple[str, str, int]]:
    """
    Extract Chrome browsing history.

    Args:
        db_path: Path to Chrome History database
        limit: Max number of entries to retrieve

    Returns:
        List of (url, title, timestamp) tuples
    """
    import shutil
    import tempfile

    try:
        if not Path(db_path).exists():
            print(f"[ERROR] History database not found: {db_path}")
            sys.exit(1)

        # Copy DB to temp file to avoid lock (Chrome keeps it open)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            temp_db = tmp.name

        try:
            shutil.copy2(db_path, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT url, title, last_visit_time FROM urls "
                "ORDER BY last_visit_time DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            return rows

        finally:
            # Clean up temp file
            if Path(temp_db).exists():
                os.unlink(temp_db)

    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


def generate_journal(db_path: str, output_dir: str = ".", limit: int = 50) -> None:
    """
    Generate markdown journal from browser history.

    Args:
        db_path: Path to Chrome History database
        output_dir: Directory for output file
        limit: Max number of entries
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    output_path = Path(output_dir) / f"journal_{today}.md"

    print(f"[INFO] Reading history from {db_path}")
    entries = get_chrome_history(db_path, limit)

    if not entries:
        print("[WARN] No history entries found")
        return

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Journal for {today}\n\n")
            for url, title, _ in entries:
                title = title or "Untitled"
                f.write(f"- [{title}]({url})\n")

        print(f"[OK] Journal generated: {output_path} ({len(entries)} entries)")

    except IOError as e:
        print(f"[ERROR] Failed to write journal: {e}")
        sys.exit(1)


def get_default_chrome_path() -> str:
    """Get default Chrome history path for current OS."""
    username = os.getenv("USERNAME") or os.getenv("USER")
    if sys.platform == "win32":
        return f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
    elif sys.platform == "darwin":
        return f"/Users/{username}/Library/Application Support/Google/Chrome/Default/History"
    else:
        return f"/home/{username}/.config/google-chrome/Default/History"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate markdown journal from Chrome browsing history"
    )
    parser.add_argument(
        "-d", "--db-path",
        default=get_default_chrome_path(),
        help="Path to Chrome History database"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Output directory for journal file (default: current dir)"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=50,
        help="Max number of entries (default: 50)"
    )

    args = parser.parse_args()
    generate_journal(args.db_path, args.output_dir, args.limit)


if __name__ == "__main__":
    main()