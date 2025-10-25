# ABOUTME: View and modify image EXIF metadata including GPS, camera settings, dates
# ABOUTME: Supports batch operations and privacy-focused metadata stripping

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif


def read_exif(image_file: str) -> Dict:
    """
    Read EXIF data from image.

    Args:
        image_file: Image file path

    Returns:
        Dictionary of EXIF data
    """
    try:
        img = Image.open(image_file)
        exif_data = img._getexif()

        if not exif_data:
            return {}

        decoded = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)

            # Handle GPS data specially
            if tag == "GPSInfo":
                gps_data = {}
                for gps_tag_id in value:
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag] = value[gps_tag_id]
                decoded[tag] = gps_data
            else:
                decoded[tag] = value

        return decoded

    except FileNotFoundError:
        print(f"[ERROR] Image file not found: {image_file}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to read EXIF: {e}")
        sys.exit(1)


def display_exif(exif_data: Dict, verbose: bool = False) -> None:
    """
    Display EXIF data in readable format.

    Args:
        exif_data: EXIF data dictionary
        verbose: Show all fields including technical data
    """
    if not exif_data:
        print("[INFO] No EXIF data found")
        return

    # Key fields to show by default
    key_fields = [
        "DateTime", "DateTimeOriginal", "Make", "Model",
        "LensModel", "FNumber", "ExposureTime", "ISOSpeedRatings",
        "FocalLength", "Flash", "WhiteBalance", "GPSInfo"
    ]

    print("\n[INFO] EXIF Data:")
    print("-" * 50)

    for field in key_fields:
        if field in exif_data:
            value = exif_data[field]
            if field == "GPSInfo" and isinstance(value, dict):
                print(f"\nGPS Information:")
                for gps_key, gps_val in value.items():
                    print(f"  {gps_key}: {gps_val}")
            else:
                print(f"{field}: {value}")

    if verbose:
        print("\n[INFO] Additional Fields:")
        for key, value in exif_data.items():
            if key not in key_fields:
                print(f"{key}: {value}")


def strip_exif(
    image_file: str,
    output_file: str = None,
    keep_orientation: bool = True
) -> None:
    """
    Remove EXIF data from image.

    Args:
        image_file: Input image file
        output_file: Output file (overwrites input if not specified)
        keep_orientation: Preserve image orientation
    """
    try:
        img = Image.open(image_file)

        # Save orientation if needed
        if keep_orientation and hasattr(img, '_getexif'):
            exif = img._getexif()
            orientation = exif.get(274) if exif else None  # 274 = Orientation tag
        else:
            orientation = None

        # Remove EXIF
        data = list(img.getdata())
        image_no_exif = Image.new(img.mode, img.size)
        image_no_exif.putdata(data)

        # Restore orientation
        if orientation:
            if orientation == 3:
                image_no_exif = image_no_exif.rotate(180, expand=True)
            elif orientation == 6:
                image_no_exif = image_no_exif.rotate(270, expand=True)
            elif orientation == 8:
                image_no_exif = image_no_exif.rotate(90, expand=True)

        output = output_file or image_file
        image_no_exif.save(output)

        print(f"[OK] EXIF data stripped from {output}")

    except Exception as e:
        print(f"[ERROR] Failed to strip EXIF: {e}")
        sys.exit(1)


def batch_strip(
    directory: str,
    output_dir: str = None,
    keep_orientation: bool = True
) -> None:
    """
    Strip EXIF from all images in directory.

    Args:
        directory: Input directory
        output_dir: Output directory (overwrites if not specified)
        keep_orientation: Preserve image orientation
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"[ERROR] Directory not found: {directory}")
        sys.exit(1)

    image_extensions = {".jpg", ".jpeg", ".png", ".tiff", ".bmp"}
    images = [f for f in dir_path.iterdir() if f.suffix.lower() in image_extensions]

    if not images:
        print("[WARN] No images found in directory")
        return

    print(f"[INFO] Found {len(images)} images")

    for img_path in images:
        if output_dir:
            output_path = Path(output_dir) / img_path.name
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = img_path

        strip_exif(str(img_path), str(output_path), keep_orientation)

    print(f"[OK] Processed {len(images)} images")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="View and modify image EXIF metadata"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # View command
    view_parser = subparsers.add_parser("view", help="View EXIF data")
    view_parser.add_argument("image", help="Image file")
    view_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show all EXIF fields"
    )

    # Strip command
    strip_parser = subparsers.add_parser("strip", help="Remove EXIF data")
    strip_parser.add_argument("image", help="Image file")
    strip_parser.add_argument(
        "-o", "--output",
        help="Output file (overwrites input if not specified)"
    )
    strip_parser.add_argument(
        "--no-orientation",
        action="store_true",
        help="Don't preserve image orientation"
    )

    # Batch strip command
    batch_parser = subparsers.add_parser("batch", help="Strip EXIF from directory")
    batch_parser.add_argument("directory", help="Input directory")
    batch_parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (overwrites if not specified)"
    )
    batch_parser.add_argument(
        "--no-orientation",
        action="store_true",
        help="Don't preserve image orientation"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "view":
        exif_data = read_exif(args.image)
        display_exif(exif_data, args.verbose)
    elif args.command == "strip":
        strip_exif(args.image, args.output, not args.no_orientation)
    elif args.command == "batch":
        batch_strip(args.directory, args.output_dir, not args.no_orientation)


if __name__ == "__main__":
    main()
