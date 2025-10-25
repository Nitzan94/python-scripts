# ABOUTME: Generate QR codes from text/URLs and scan QR codes from images
# ABOUTME: Supports batch generation from CSV and various output formats

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Tuple
import qrcode
from PIL import Image

try:
    from pyzbar.pyzbar import decode
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    try:
        import cv2
        SCANNER_AVAILABLE = "opencv"
    except ImportError:
        pass


def generate_qr(
    data: str,
    output_file: str = "qrcode.png",
    size: int = 10,
    border: int = 4
) -> None:
    """
    Generate QR code from text/URL.

    Args:
        data: Text or URL to encode
        output_file: Output image filename
        size: Box size (default: 10)
        border: Border size in boxes (default: 4)
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_file)

        print(f"[OK] QR code generated: {output_file}")
        print(f"[INFO] Encoded: {data[:50]}{'...' if len(data) > 50 else ''}")

    except Exception as e:
        print(f"[ERROR] Failed to generate QR code: {e}")
        sys.exit(1)


def batch_generate(csv_file: str, output_dir: str = "qrcodes") -> None:
    """
    Generate QR codes from CSV file.

    Args:
        csv_file: CSV file with 'data' and optional 'filename' columns
        output_dir: Output directory for QR codes
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if "data" not in reader.fieldnames:
                print("[ERROR] CSV must have 'data' column")
                sys.exit(1)

            count = 0
            for i, row in enumerate(reader, 1):
                data = row["data"]
                filename = row.get("filename", f"qr_{i}.png")

                if not filename.endswith(".png"):
                    filename += ".png"

                output_file = output_path / filename
                generate_qr(data, str(output_file))
                count += 1

        print(f"[OK] Generated {count} QR codes in {output_dir}")

    except FileNotFoundError:
        print(f"[ERROR] CSV file not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Batch generation failed: {e}")
        sys.exit(1)


def scan_qr(image_file: str) -> List[str]:
    """
    Scan QR code from image.

    Args:
        image_file: Image file to scan

    Returns:
        List of decoded data strings
    """
    if not SCANNER_AVAILABLE:
        print("[ERROR] QR scanning not available")
        print("[INFO] Install scanner library:")
        print("  Option 1: pip install pyzbar (requires ZBar DLL on Windows)")
        print("  Option 2: pip install opencv-python")
        sys.exit(1)

    try:
        if not Path(image_file).exists():
            print(f"[ERROR] Image file not found: {image_file}")
            sys.exit(1)

        if SCANNER_AVAILABLE == "opencv":
            # Use OpenCV QR detector
            import cv2
            img = cv2.imread(image_file)
            detector = cv2.QRCodeDetector()
            data, vertices, _ = detector.detectAndDecode(img)

            if not data:
                print("[WARN] No QR codes found in image")
                return []

            print(f"[OK] Decoded: {data}")
            return [data]
        else:
            # Use pyzbar
            img = Image.open(image_file)
            decoded_objects = decode(img)

            if not decoded_objects:
                print("[WARN] No QR codes found in image")
                return []

            results = []
            for obj in decoded_objects:
                data = obj.data.decode("utf-8")
                results.append(data)
                print(f"[OK] Decoded: {data}")
                print(f"[INFO] Type: {obj.type}")

            return results

    except Exception as e:
        print(f"[ERROR] Failed to scan QR code: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and scan QR codes"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate QR code")
    gen_parser.add_argument("data", help="Text or URL to encode")
    gen_parser.add_argument(
        "-o", "--output",
        default="qrcode.png",
        help="Output filename (default: qrcode.png)"
    )
    gen_parser.add_argument(
        "-s", "--size",
        type=int,
        default=10,
        help="Box size (default: 10)"
    )
    gen_parser.add_argument(
        "-b", "--border",
        type=int,
        default=4,
        help="Border size (default: 4)"
    )

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch generate from CSV")
    batch_parser.add_argument("csv", help="CSV file with 'data' column")
    batch_parser.add_argument(
        "-o", "--output-dir",
        default="qrcodes",
        help="Output directory (default: qrcodes)"
    )

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan QR code from image")
    scan_parser.add_argument("image", help="Image file to scan")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "generate":
        generate_qr(args.data, args.output, args.size, args.border)
    elif args.command == "batch":
        batch_generate(args.csv, args.output_dir)
    elif args.command == "scan":
        scan_qr(args.image)


if __name__ == "__main__":
    main()
