"""OCR pipeline for adding a selectable text layer to image-only PDFs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfWriter

REQUIRED_BINARIES = ("tesseract", "pdftoppm")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    return parser.parse_args(argv)


def ensure_dependencies() -> None:
    missing = [binary for binary in REQUIRED_BINARIES if shutil.which(binary) is None]
    if missing:
        raise RuntimeError(
            "Missing required system binaries: "
            + ", ".join(missing)
            + ". Install Tesseract OCR and Poppler."
        )


def run_tesseract(image_path: Path, output_base: Path, lang: str) -> Path:
    cmd = ["tesseract", str(image_path), str(output_base), "-l", lang, "pdf"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Tesseract failed on {image_path.name}:\n{details}")

    return output_base.with_suffix(".pdf")


def run_pipeline(input_pdf: Path, output_pdf: Path, dpi: int, lang: str) -> None:
    with tempfile.TemporaryDirectory(prefix="readablepdf_") as tmp_dir:
        temp_root = Path(tmp_dir)
        image_dir = temp_root / "images"
        ocr_dir = temp_root / "ocr"
        image_dir.mkdir(parents=True, exist_ok=True)
        ocr_dir.mkdir(parents=True, exist_ok=True)

        print(f"Rasterizing pages from: {input_pdf}")
        image_paths = convert_from_path(
            pdf_path=str(input_pdf),
            dpi=dpi,
            fmt="png",
            output_folder=str(image_dir),
            paths_only=True,
        )

        if not image_paths:
            raise RuntimeError("No pages found in the PDF.")

        page_pdfs: list[Path] = []
        total = len(image_paths)

        for idx, image_path in enumerate(image_paths, start=1):
            image_path = Path(image_path)
            print(f"OCR page {idx}/{total}: {image_path.name}")
            output_base = ocr_dir / f"page_{idx:04d}"
            page_pdf = run_tesseract(image_path, output_base, lang)
            page_pdfs.append(page_pdf)

        print(f"Merging {len(page_pdfs)} OCR pages into: {output_pdf}")
        writer = PdfWriter()
        for page_pdf in page_pdfs:
            writer.append(str(page_pdf))
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        with output_pdf.open("wb") as out_f:
            writer.write(out_f)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

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
        run_pipeline(input_pdf=input_pdf, output_pdf=output_pdf, dpi=args.dpi, lang=args.lang)
    except RuntimeError as err:
        print(err, file=sys.stderr)
        return 1

    print("Done.")
    return 0
