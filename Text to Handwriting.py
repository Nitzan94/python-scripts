# ABOUTME: Converts typed text to realistic handwriting images
# ABOUTME: Supports multiple handwriting styles, colors, and paper backgrounds

import argparse
import sys
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
import random


def create_handwriting_image(
    text: str,
    output_file: str = "handwriting.png",
    font_size: int = 40,
    line_spacing: int = 60,
    ink_color: Tuple[int, int, int] = (0, 0, 139),
    paper_color: Tuple[int, int, int] = (255, 255, 240),
    width: int = 800,
    margin: int = 50,
    variation: bool = True
) -> None:
    """
    Create handwriting-style image from text.

    Args:
        text: Text to convert
        output_file: Output image filename
        font_size: Base font size
        line_spacing: Space between lines
        ink_color: RGB tuple for ink color
        paper_color: RGB tuple for paper background
        width: Image width
        margin: Page margins
        variation: Add random variations for realism
    """
    try:
        # Try to use a handwriting-like font
        font_paths = [
            "C:/Windows/Fonts/segoepr.ttf",  # Segoe Print (Windows)
            "C:/Windows/Fonts/comic.ttf",     # Comic Sans (fallback)
            "/System/Library/Fonts/MarkerFelt.ttc",  # Mac
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"  # Linux
        ]

        font = None
        for font_path in font_paths:
            if Path(font_path).exists():
                font = ImageFont.truetype(font_path, font_size)
                break

        if not font:
            print("[WARN] Handwriting font not found, using default font")
            font = ImageFont.load_default()

        # Split text into lines
        lines = text.split("\n")

        # Calculate image height
        height = margin * 2 + (len(lines) * line_spacing)

        # Create image
        img = Image.new("RGB", (width, height), paper_color)
        draw = ImageDraw.Draw(img)

        # Draw text with variations
        y_pos = margin
        for line in lines:
            x_pos = margin

            if variation:
                # Add slight random vertical offset for natural look
                y_offset = random.randint(-2, 2)
            else:
                y_offset = 0

            # Draw the line
            draw.text(
                (x_pos, y_pos + y_offset),
                line,
                font=font,
                fill=ink_color
            )

            y_pos += line_spacing

        # Save image
        img.save(output_file)
        print(f"[OK] Handwriting image saved to {output_file}")

    except Exception as e:
        print(f"[ERROR] Failed to create handwriting: {e}")
        sys.exit(1)


def parse_color(color_str: str) -> Tuple[int, int, int]:
    """
    Parse color string to RGB tuple.

    Args:
        color_str: Color name or hex code

    Returns:
        RGB tuple
    """
    color_map = {
        "black": (0, 0, 0),
        "blue": (0, 0, 139),
        "darkblue": (0, 0, 139),
        "navy": (0, 0, 128),
        "red": (139, 0, 0),
        "green": (0, 100, 0),
        "purple": (128, 0, 128),
        "brown": (101, 67, 33),
        "white": (255, 255, 255),
        "cream": (255, 255, 240),
        "ivory": (255, 255, 240)
    }

    color_lower = color_str.lower()

    # Check color map
    if color_lower in color_map:
        return color_map[color_lower]

    # Try hex code
    if color_str.startswith("#"):
        hex_str = color_str.lstrip("#")
        try:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        except:
            pass

    print(f"[WARN] Unknown color '{color_str}', using default")
    return (0, 0, 139)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert text to handwriting-style images"
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to convert (or use -f for file input)"
    )
    parser.add_argument(
        "-f", "--file",
        help="Read text from file"
    )
    parser.add_argument(
        "-o", "--output",
        default="handwriting.png",
        help="Output image filename (default: handwriting.png)"
    )
    parser.add_argument(
        "-s", "--font-size",
        type=int,
        default=40,
        help="Font size (default: 40)"
    )
    parser.add_argument(
        "-l", "--line-spacing",
        type=int,
        default=60,
        help="Line spacing (default: 60)"
    )
    parser.add_argument(
        "-c", "--ink-color",
        default="darkblue",
        help="Ink color (name or hex code, default: darkblue)"
    )
    parser.add_argument(
        "-p", "--paper-color",
        default="cream",
        help="Paper color (name or hex code, default: cream)"
    )
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=800,
        help="Image width (default: 800)"
    )
    parser.add_argument(
        "--no-variation",
        action="store_true",
        help="Disable random variations"
    )

    args = parser.parse_args()

    # Get text
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"[ERROR] File not found: {args.file}")
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("[ERROR] Provide text or use -f to specify input file")
        parser.print_help()
        sys.exit(1)

    # Parse colors
    ink_color = parse_color(args.ink_color)
    paper_color = parse_color(args.paper_color)

    # Create handwriting
    create_handwriting_image(
        text,
        args.output,
        args.font_size,
        args.line_spacing,
        ink_color,
        paper_color,
        args.width,
        variation=not args.no_variation
    )


if __name__ == "__main__":
    main()
