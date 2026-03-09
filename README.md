# readablepdf

`readablepdf` converts image-only PDFs into searchable and selectable PDFs by adding an OCR text layer while preserving page visuals.

## How it works

1. Render each page to a PNG (`pdf2image` backed by Poppler).
2. OCR each page with Tesseract in PDF mode (image layer + invisible text layer).
3. Merge all OCR page PDFs into one output PDF.

All intermediate files are written inside an OS temporary directory and removed automatically.

## System dependencies (Linux + macOS)

You need these binaries on the machine where you run `readablepdf`:

- `tesseract`
- `pdftoppm` (from Poppler)

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y tesseract-ocr poppler-utils
```

macOS (Homebrew):

```bash
brew install tesseract poppler
```

If you need languages beyond English, install matching Tesseract language packs.

## Install and run with pipx

Once published on PyPI, you can run it directly without managing a virtualenv:

```bash
pipx run readablepdf input.pdf
```

Custom output/language/DPI:

```bash
pipx run readablepdf input.pdf -o output_ocr.pdf --lang eng --dpi 200
```

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
ruff check .
ruff format --check .
pytest -q
python -m build
```

## GitHub Actions

- `CI` workflow: lint + format check + tests + build on Ubuntu and macOS.
- `Publish to PyPI` workflow: runs on GitHub Release publish (and manual trigger).

### GitHub configuration needed for publish

1. Create repository secret: `PYPI_API_TOKEN`.
2. Set it to a PyPI API token with upload permission for this project.
3. (Optional but recommended) create a protected environment named `pypi` and require approvals.

## Release flow

1. Merge to `main`.
2. Create a Git tag/release (for example `v0.1.1`).
3. `Publish to PyPI` workflow uploads artifacts to PyPI with version derived from that tag.
