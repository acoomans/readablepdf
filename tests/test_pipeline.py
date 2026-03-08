from pathlib import Path

from readablepdf import pipeline


def test_default_output_path(tmp_path: Path) -> None:
    input_pdf = tmp_path / "sample.pdf"
    input_pdf.write_bytes(b"pdf")
    args = pipeline.parse_args([str(input_pdf)])

    output = (
        input_pdf.with_name(f"{input_pdf.stem}_ocr.pdf") if args.output is None else args.output
    )
    assert output.name == "sample_ocr.pdf"


def test_missing_binary_reports_error(monkeypatch) -> None:
    monkeypatch.setattr(pipeline.shutil, "which", lambda _cmd: None)

    try:
        pipeline.ensure_dependencies()
    except RuntimeError as err:
        message = str(err)
    else:
        raise AssertionError("expected RuntimeError")

    assert "tesseract" in message
    assert "pdftoppm" in message
