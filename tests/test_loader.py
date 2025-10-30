# tests/test_loader.py

from pathlib import Path
import pytest


# Adjust this to match your module path, e.g. "project_recommender.loader"
MODULE = "src.project_recommender.loader"


# Import target module
try:
    loader = __import__(MODULE, fromlist=["*"])
except Exception as e:
    raise ImportError(
        f"Could not import module {MODULE!r}. Update MODULE at top of this test file "
        "(e.g. 'projects_recommend.loader' or 'src.project_recommender.loader').\n"
        f"Original error: {e!r}"
    )

# Tests
def _make_pdf(path: Path, name: str):
    """Create a dummy PDF file (not a valid PDF but good enough for testing rglob)."""
    p = path / name
    p.write_bytes(b"%PDF-1.4\n% Dummy PDF content\n")
    return p


def test_move_pdf_copies_pdfs_good(tmp_path, monkeypatch):
    """
    Good case:
      - create a fake module directory structure under tmp_path/src/...
      - create data/raw_PDFs under the expected two-up location
      - create a folder with PDFs and call move_pdf
      - assert returned dict and files are copied
    """
    # Arrange: create fake layout for module __file__
    # e.g. tmp_path / "src" / "pkg" / "loader.py"
    src_dir = tmp_path / "src"
    pkg_dir = src_dir / "pkg"
    pkg_dir.mkdir(parents=True)
    fake_loader_file = pkg_dir / "loader.py"
    fake_loader_file.write_text("# fake loader file for tests\n")

    # Create the "two_up" location = dirname(dirname(filepath_resolved_folder)) => src_dir
    # In src_dir create data/raw_PDFs
    data_dir = tmp_path/ "data"
    raw_pdfs_dir = data_dir / "raw_PDFs"
    raw_pdfs_dir.mkdir(parents=True)

    # Create an input folder that contains some PDFs
    input_folder = tmp_path / "incoming_pdfs"
    input_folder.mkdir()
    pdf1 = _make_pdf(input_folder, "a.pdf")
    pdf2 = _make_pdf(input_folder, "b.pdf")

    # Monkeypatch the module's __file__ so the function computes two_up relative to our tmp structure
    monkeypatch.setattr(loader, "__file__", str(fake_loader_file))

    # Act
    result = loader.move_pdf(str(input_folder))

    # Assert returned dictionary and copy counts
    assert isinstance(result, dict)
    assert "Copied files" in result
    assert result["Number of files copied"] == 2

    # Files should exist in the raw_pdfs_dir
    dest_files = [raw_pdfs_dir / "a.pdf", raw_pdfs_dir / "b.pdf"]
    for df in dest_files:
        assert df.exists()
        # verify bytes copied match original
        assert df.read_bytes() == (input_folder / df.name).read_bytes()


def test_move_pdf_no_pdfs_returns_message(tmp_path, monkeypatch):
    """
    If the input folder contains no PDFs, the function returns the specific message string.
    """
    # Setup fake module location
    src_dir = tmp_path / "src2"
    pkg_dir = src_dir / "pkg"
    pkg_dir.mkdir(parents=True)
    fake_loader_file = pkg_dir / "loader.py"
    fake_loader_file.write_text("")

    # Create input folder with no pdfs
    input_folder = tmp_path / "empty_incoming"
    input_folder.mkdir()

    # Create expected data/raw_PDFs under two_up so that the function can reach the data dir
    data_dir = src_dir / "data"
    raw_pdfs_dir = data_dir / "raw_PDFs"
    raw_pdfs_dir.mkdir(parents=True)

    monkeypatch.setattr(loader, "__file__", str(fake_loader_file))

    res = loader.move_pdf(str(input_folder))
    assert isinstance(res, str)
    assert "There are no PDFs" in res


def test_move_pdf_no_data_dir_returns_message(tmp_path, monkeypatch):
    """
    If the code cannot find a 'data' directory under two_up, it returns the specific message.
    """
    # Setup fake module location where two_up has no data directory
    src_dir = tmp_path / "src3"
    pkg_dir = src_dir / "pkg"
    pkg_dir.mkdir(parents=True)
    fake_loader_file = pkg_dir / "loader.py"
    fake_loader_file.write_text("")

    # Input folder with a PDF so it gets past the PDF-finding stage
    input_folder = tmp_path / "incoming3"
    input_folder.mkdir()
    _make_pdf(input_folder, "x.pdf")

    # Ensure no 'data' directory exists under two_up (which will be src_dir)
    # (we purposely do NOT create src_dir / "data")

    monkeypatch.setattr(loader, "__file__", str(fake_loader_file))

    res = loader.move_pdf(str(input_folder))
    assert isinstance(res, str)
    assert "There is no data directory" in res


def test_move_pdf_no_raw_pdfs_dir_returns_message(tmp_path, monkeypatch):
    """
    If data exists but raw_PDFs is missing, expect the specific message.
    """
    # Setup fake module location
    src_dir = tmp_path / "src4"
    pkg_dir = src_dir / "pkg"
    pkg_dir.mkdir(parents=True)
    fake_loader_file = pkg_dir / "loader.py"
    fake_loader_file.write_text("")

    # Create data but omit raw_PDFs
    data_dir = tmp_path/ "data"
    data_dir.mkdir(parents=True)
    # (do not create raw_PDFs)

    # create input folder with one pdf
    input_folder = tmp_path / "incoming4"
    input_folder.mkdir()
    _make_pdf(input_folder, "x.pdf")

    monkeypatch.setattr(loader, "__file__", str(fake_loader_file))

    res = loader.move_pdf(str(input_folder))
    assert isinstance(res, str)
    assert "There is no raw_PDFs directory" in res


def test_move_pdf_null_input_raises(monkeypatch):
    """
    Passing None as filepath should raise a TypeError when Path(...) is called.
    """
    # set module __file__ to something valid so the function gets past file-folder logic
    # create a temp fake file path in memory (no actual file required here)
    fake_loader_file = "/tmp/fakepkg/loader.py"
    monkeypatch.setattr(loader, "__file__", fake_loader_file)

    with pytest.raises(Exception) as exc:
        loader.move_pdf(None)

    # Accept TypeError or ValueError depending on Path implementation
    assert isinstance(exc.value, (TypeError, ValueError))


