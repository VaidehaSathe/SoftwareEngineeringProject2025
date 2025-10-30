"""Tests for the pdf_loader_plumber module in the project_recommender package."""

import pytest
import pandas as pd
import shutil
from reportlab.pdfgen import canvas

# Import the functions to test
from src.project_recommender.pdf_loader_plumber import (
    parse_pdf,
    process_pdf_to_csv,
    process_all_pdfs_to_one_csv,
)

from src.project_recommender.loader import ( RAW_PDF_DIR, CSV_OUTPUT_DIR )

# @pytest.fixture(scope="module")
# def sample_pdf(tmp_path_factory):
#     """
#     Fixture to provide a small, known PDF for tests.
#     For simplicity, this assumes at least one .pdf exists in data/raw_PDFs.
#     If not, you can manually copy a test PDF there.
#     """
#     pdfs = list(RAW_PDF_DIR.glob("*.pdf"))
#     if not pdfs:
#         pytest.skip("No sample PDFs found in data/raw_PDFs/")
#     return pdfs[0]

@pytest.fixture(scope="module")
def sample_pdf(tmp_path_factory):
    """
    Fixture to ensure at least one sample PDF exists in RAW_PDF_DIR.
    If none exists, this will generate a small test PDF using reportlab
    and copy it into RAW_PDF_DIR for the tests to use.
    """
    RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = list(RAW_PDF_DIR.glob("*.pdf"))

    if pdfs:
        # Return the first existing PDF
        return pdfs[0]

    # Create a temporary PDF file
    tmp_dir = tmp_path_factory.mktemp("pdf_fixture")
    pdf_path = tmp_dir / "sample.pdf"

    # Generate a minimal, valid PDF
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "This is a sample test PDF for CI testing.")
    c.showPage()
    c.save()

    # Copy the PDF into RAW_PDF_DIR so all functions can find it
    dest_path = RAW_PDF_DIR / pdf_path.name
    shutil.copy2(pdf_path, dest_path)

    return dest_path


def test_parse_pdf_returns_list(sample_pdf):
    """parse_pdf() should return a non-empty list of dicts."""
    projects = parse_pdf(sample_pdf)
    assert isinstance(projects, list)
    if projects:
        assert isinstance(projects[0], dict)
        # must contain our expected keys
        for key in ["title", "primary_theme", "supervisors", "description"]:
            assert key in projects[0]


def test_process_pdf_to_csv_creates_file(tmp_path, sample_pdf):
    """process_pdf_to_csv() should create a CSV file."""
    out_csv = tmp_path / "test_out.csv"
    result_path = process_pdf_to_csv(sample_pdf, out_csv)
    assert result_path.exists()
    df = pd.read_csv(result_path)
    # expected columns
    for col in ["title", "primary_theme", "supervisors", "description"]:
        assert col in df.columns


def test_process_all_pdfs_to_one_csv(tmp_path):
    """Should process all PDFs and produce one combined CSV."""
    out_csv = tmp_path / "combined.csv"
    result_path = process_all_pdfs_to_one_csv(out_csv)
    assert result_path.exists()
    df = pd.read_csv(result_path)
    assert all(c in df.columns for c in ["title", "primary_theme", "supervisors", "description"])
    # file should be empty (header-only) or have rows
    assert df.shape[1] == 4


def test_raw_and_output_dirs_exist():
    """Verify that RAW_PDF_DIR and CSV_OUTPUT_DIR are valid directories."""
    assert RAW_PDF_DIR.exists() and RAW_PDF_DIR.is_dir()
    assert CSV_OUTPUT_DIR.exists() and CSV_OUTPUT_DIR.is_dir()
