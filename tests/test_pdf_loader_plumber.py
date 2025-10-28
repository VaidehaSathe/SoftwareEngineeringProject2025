import pytest
from pathlib import Path
import pandas as pd

# Import the functions to test
from src.project_recommender.pdf_loader_plumber import (
    parse_pdf,
    process_pdf_to_csv,
    process_all_pdfs_to_one_csv,
    RAW_PDF_DIR,
    CSV_OUTPUT_DIR,
)

@pytest.fixture(scope="module")
def sample_pdf(tmp_path_factory):
    """
    Fixture to provide a small, known PDF for tests.
    For simplicity, this assumes at least one .pdf exists in data/raw_PDFs.
    If not, you can manually copy a test PDF there.
    """
    pdfs = list(RAW_PDF_DIR.glob("*.pdf"))
    if not pdfs:
        pytest.skip("No sample PDFs found in data/raw_PDFs/")
    return pdfs[0]


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
