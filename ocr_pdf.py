#!/usr/bin/env python3
"""Add a selectable OCR text layer to an image-based PDF using Tesseract.

Workflow:
1. Rasterize each PDF page to an image (via pdf2image + Poppler).
2. OCR each image with Tesseract in PDF output mode.
3. Merge the per-page OCR PDFs into one final output file.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfWriter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a searchable/annotatable PDF by OCRing an image-only PDF."
    )
    parser.add_argument("input_pdf", type=Path, help="Path to input PDF")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PDF path (default: <input_stem>_ocr.pdf)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Rasterization DPI for OCR input images (default: 200)",
    )
    parser.add_argument(
        "--lang",
        default="eng",
        help="Tesseract language(s), e.g. 'eng' or 'eng+fra' (default: eng)",
    )
    return parser.parse_args()


def ensure_dependencies() -> None:
    missing = []
    for cmd in ("tesseract", "pdftoppm"):
        if shutil.which(cmd) is None:
            missing.append(cmd)

    if missing:
        raise RuntimeError(
            "Missing required system binaries: "
            + ", ".join(missing)
            + ". Install Tesseract OCR and Poppler."
        )


def run_tesseract(image_path: Path, output_base: Path, lang: str) -> Path:
    cmd = [
        "tesseract",
        str(image_path),
        str(output_base),
        "-l",
        lang,
        "pdf",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Tesseract failed on {image_path.name}:\n{result.stderr.strip() or result.stdout.strip()}"
        )

    return output_base.with_suffix(".pdf")


def main() -> int:
    args = parse_args()

    input_pdf = args.input_pdf.expanduser().resolve()
    if not input_pdf.exists():
        print(f"Input file does not exist: {input_pdf}", file=sys.stderr)
        return 1

    if args.output is None:
        output_pdf = input_pdf.with_name(f"{input_pdf.stem}_ocr.pdf")
    else:
        output_pdf = args.output.expanduser().resolve()

    try:
        ensure_dependencies()
    except RuntimeError as err:
        print(err, file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ocr_pdf_") as tmp_dir:
        temp_root = Path(tmp_dir)
        image_dir = temp_root / "images"
        ocr_dir = temp_root / "ocr"
        image_dir.mkdir(parents=True, exist_ok=True)
        ocr_dir.mkdir(parents=True, exist_ok=True)

        print(f"Rasterizing pages from: {input_pdf}")
        image_paths = convert_from_path(
            pdf_path=str(input_pdf),
            dpi=args.dpi,
            fmt="png",
            output_folder=str(image_dir),
            paths_only=True,
        )

        if not image_paths:
            print("No pages found in the PDF.", file=sys.stderr)
            return 1

        page_pdfs: list[Path] = []
        total = len(image_paths)

        for idx, image_path in enumerate(image_paths, start=1):
            image_path = Path(image_path)
            print(f"OCR page {idx}/{total}: {image_path.name}")
            output_base = ocr_dir / f"page_{idx:04d}"
            page_pdf = run_tesseract(image_path, output_base, args.lang)
            page_pdfs.append(page_pdf)

        print(f"Merging {len(page_pdfs)} OCR pages into: {output_pdf}")
        writer = PdfWriter()
        for page_pdf in page_pdfs:
            writer.append(str(page_pdf))
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        with output_pdf.open("wb") as out_f:
            writer.write(out_f)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
