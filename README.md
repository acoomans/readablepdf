# readablepdf

This repository contains a script that converts an image-only PDF into a searchable/annotatable PDF.

It does this by:
1. Rendering each page to an image (`pdf2image` + Poppler).
2. Running Tesseract OCR per page in PDF mode (keeps original image + adds invisible text layer).
3. Merging all OCR-generated page PDFs into one final PDF (`pypdf`).

## Files

- `ocr_pdf.py`: main automation script.
- `requirements.txt`: Python dependencies.
- `.gitignore`: ignores generated files and virtual env files.

## Prerequisites

### System packages

Install Tesseract OCR and Poppler utilities.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y tesseract-ocr poppler-utils python3-venv
```

If your PDF language is not English, also install the matching Tesseract language package(s), for example:

```bash
sudo apt install -y tesseract-ocr-fra
```

macOS (Homebrew):

```bash
brew install tesseract poppler
```

### Python environment

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Basic usage (creates `<input_stem>_ocr.pdf` next to input):

```bash
python ocr_pdf.py input.pdf
```

Custom output:

```bash
python ocr_pdf.py input.pdf -o output_ocr.pdf
```

Custom OCR options:

```bash
python ocr_pdf.py input.pdf --dpi 200 --lang eng
```

- `--dpi` controls the rendered image quality used for OCR.
- `--lang` is the Tesseract language string (examples: `eng`, `eng+fra`).

## Notes

- Higher DPI may improve OCR quality but increases processing time and output size.
- The script checks that `tesseract` and `pdftoppm` are installed before running.
- If you prefer a single external tool, `ocrmypdf --skip-text input.pdf output.pdf` is an alternative.
