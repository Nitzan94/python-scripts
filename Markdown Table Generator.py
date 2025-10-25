# ABOUTME: Converts CSV/JSON data to markdown tables with formatting
# ABOUTME: Supports alignment, auto-formatting, and GitHub-flavored markdown

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def format_table(
    data: List[List[str]],
    headers: List[str],
    alignment: List[str] = None
) -> str:
    """
    Format data as markdown table.

    Args:
        data: Table data rows
        headers: Column headers
        alignment: List of 'left', 'center', 'right' for each column

    Returns:
        Markdown table string
    """
    if not alignment:
        alignment = ["left"] * len(headers)

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Build table
    lines = []

    # Header row
    header_cells = [f" {h:<{widths[i]}} " for i, h in enumerate(headers)]
    lines.append("|" + "|".join(header_cells) + "|")

    # Separator row
    sep_cells = []
    for i, align in enumerate(alignment):
        width = widths[i]
        if align == "center":
            sep = f":{'-' * width}:"
        elif align == "right":
            sep = f"{'-' * (width + 1)}:"
        else:  # left
            sep = f":{'-' * (width + 1)}"
        sep_cells.append(sep)
    lines.append("|" + "|".join(sep_cells) + "|")

    # Data rows
    for row in data:
        cells = [f" {str(cell):<{widths[i]}} " for i, cell in enumerate(row)]
        lines.append("|" + "|".join(cells) + "|")

    return "\n".join(lines)


def csv_to_markdown(
    csv_file: str,
    alignment: str = None,
    output_file: str = None
) -> str:
    """
    Convert CSV to markdown table.

    Args:
        csv_file: Input CSV file
        alignment: Alignment string (e.g., 'lcr' for left,center,right)
        output_file: Output file path (optional)

    Returns:
        Markdown table string
    """
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            print("[ERROR] CSV file is empty")
            sys.exit(1)

        headers = rows[0]
        data = rows[1:]

        # Parse alignment
        align_map = {"l": "left", "c": "center", "r": "right"}
        if alignment:
            alignments = [align_map.get(a.lower(), "left") for a in alignment]
        else:
            alignments = None

        table = format_table(data, headers, alignments)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(table)
            print(f"[OK] Markdown table saved to {output_file}")
        else:
            print(table)

        return table

    except FileNotFoundError:
        print(f"[ERROR] CSV file not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to convert CSV: {e}")
        sys.exit(1)


def json_to_markdown(
    json_file: str,
    alignment: str = None,
    output_file: str = None
) -> str:
    """
    Convert JSON to markdown table.

    Args:
        json_file: Input JSON file (array of objects)
        alignment: Alignment string
        output_file: Output file path (optional)

    Returns:
        Markdown table string
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        if not isinstance(json_data, list):
            print("[ERROR] JSON must be an array of objects")
            sys.exit(1)

        if not json_data:
            print("[ERROR] JSON array is empty")
            sys.exit(1)

        # Extract headers from first object
        headers = list(json_data[0].keys())

        # Extract data rows
        data = [[str(obj.get(h, "")) for h in headers] for obj in json_data]

        # Parse alignment
        align_map = {"l": "left", "c": "center", "r": "right"}
        if alignment:
            alignments = [align_map.get(a.lower(), "left") for a in alignment]
        else:
            alignments = None

        table = format_table(data, headers, alignments)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(table)
            print(f"[OK] Markdown table saved to {output_file}")
        else:
            print(table)

        return table

    except FileNotFoundError:
        print(f"[ERROR] JSON file not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to convert JSON: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert CSV/JSON to markdown tables"
    )
    parser.add_argument(
        "input",
        help="Input file (CSV or JSON)"
    )
    parser.add_argument(
        "-a", "--alignment",
        help="Column alignment (e.g., 'lcr' = left,center,right). Use 'l', 'c', or 'r' for each column"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output markdown file (optional, prints to console if not specified)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] File not found: {args.input}")
        sys.exit(1)

    if input_path.suffix.lower() == ".csv":
        csv_to_markdown(args.input, args.alignment, args.output)
    elif input_path.suffix.lower() == ".json":
        json_to_markdown(args.input, args.alignment, args.output)
    else:
        print("[ERROR] File must be .csv or .json")
        sys.exit(1)


if __name__ == "__main__":
    main()
