"""Tests for the preprocessor module in the project_recommender package."""

import pytest
import pandas as pd
from src.project_recommender import preprocessor as ppr

# Fixtures and test utilities

@pytest.fixture(autouse=True)
def setup(monkeypatch):
    """Ensure nltk calls are safe (no downloads needed) during tests."""
    monkeypatch.setattr(ppr.nltk, "word_tokenize", lambda text: text.split())
    monkeypatch.setattr(ppr.nltk, "pos_tag", lambda words: [(w, "NN") for w in words])
    ppr.stop_words = set(["a", "the", "is"])  # simplify
    yield


# Query Preprocessor Tests

def test_query_preprocessor_good_data():
    """Should preprocess normal string correctly."""
    text = "Cats are running"
    result = ppr.query_preprocessor(text)
    # Basic sanity checks
    assert isinstance(result, str)
    assert "cats" in result or "cat" in result


def test_query_preprocessor_empty_string():
    """Should handle empty string gracefully."""
    result = ppr.query_preprocessor("")
    assert result == ""


def test_query_preprocessor_non_string_input():
    """Should raise an error or handle non-string input."""
    with pytest.raises(AttributeError):
        # Because .lower() is called on input
        ppr.query_preprocessor(None)


# Data Preprocessor Tests

def test_data_preprocessor_good_data(tmp_path, monkeypatch):
    """Should read a CSV, process it, and write a new tokenized CSV."""

    # Create temporary folder structure
    input_dir = tmp_path / "data" / "project_CSVs"
    output_dir = tmp_path / "data" / "tokenized_CSVs"
    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    # Create a dummy input CSV
    filename = "projects.csv"
    input_file = input_dir / filename
    df_in = pd.DataFrame({
        "title": ["Book 1", "Book 2"],
        "description": ["This is the first project", "Second project description"]
    })
    df_in.to_csv(input_file, index=False)

    # Monkeypatch working directory to tmp_path
    monkeypatch.chdir(tmp_path)

    # Monkeypatch preprocess_text for predictability
    monkeypatch.setattr(ppr, "preprocess_text", lambda s: s.upper())

    # Run the function
    ppr.data_preprocessor(filename)

    # Check that the expected output file was created
    output_file = output_dir / f"tokenized_{filename}"
    assert output_file.exists(), f"Expected output file not found: {output_file}"

    # Verify the file’s contents
    df_out = pd.read_csv(output_file)
    assert "tokenized_description" in df_out.columns
    # preprocess_text was patched to .upper(), so the output should be uppercase
    assert df_out["tokenized_description"].iloc[0] == "THIS IS THE FIRST PROJECT"
    assert df_out["tokenized_description"].iloc[1] == "SECOND PROJECT DESCRIPTION"


def test_data_preprocessor_missing_file(tmp_path, monkeypatch):
    """Should raise FileNotFoundError if input CSV doesn't exist."""
    base = tmp_path / "data"
    (base / "project_CSVs").mkdir(parents=True)
    (base / "tokenized_CSVs").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        ppr.data_preprocessor("nonexistent.csv")


# def test_data_preprocessor_null_description(tmp_path, monkeypatch):
#     """Should handle null or NaN values in the description column gracefully."""

#     # Create temporary folder structure
#     input_dir = tmp_path / "data" / "project_CSVs"
#     output_dir = tmp_path / "data" / "tokenized_CSVs"
#     input_dir.mkdir(parents=True)
#     output_dir.mkdir(parents=True)

#     # Create a dummy CSV with one normal and one null description
#     filename = "projects.csv"
#     input_file = input_dir / filename
#     df_in = pd.DataFrame({
#         "title": ["Book 1", "Book 2"],
#         "description": ["This is a project", None]  # one valid, one None
#     })
#     df_in.to_csv(input_file, index=False)

#     # Monkeypatch working directory to tmp_path
#     monkeypatch.chdir(tmp_path)

#     # Monkeypatch preprocess_text to handle None gracefully
#     def safe_preprocess(text):
#         if text is None or not isinstance(text, str):
#             return ""
#         return text.upper()

#     monkeypatch.setattr(ppr, "preprocess_text", safe_preprocess)

#     # Run the function
#     ppr.data_preprocessor(filename)

#     # Check that the expected output file was created
#     output_file = output_dir / f"tokenized_{filename}"
#     assert output_file.exists(), f"Expected output file not found: {output_file}"

#     # Verify the output CSV contents
#     df_out = pd.read_csv(output_file)

#     # Confirm that the tokenized_description column exists
#     assert "tokenized_description" in df_out.columns

#     # The first row should be uppercase, the second should be empty
#     assert df_out["tokenized_description"].iloc[0] == "THIS IS A PROJECT"
#     # Pandas might interpret an empty field as NaN, so handle both cases
#     val = df_out["tokenized_description"].iloc[1]
#     assert pd.isna(val) or val == ""

def test_data_preprocessor_null_description(tmp_path, monkeypatch):
    """Should handle null or NaN values in the description column gracefully."""

    # Create temporary folder structure
    input_dir = tmp_path / "data" / "project_CSVs"
    output_dir = tmp_path / "data" / "tokenized_CSVs"
    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    # Create a dummy CSV with one normal and one null description
    filename = "projects.csv"
    input_file = input_dir / filename
    df_in = pd.DataFrame({
        "title": ["Book 1", "Book 2"],
        "description": ["This is a project", None]  # one valid, one None
    })
    df_in.to_csv(input_file, index=False)

    # Monkeypatch working directory to tmp_path
    monkeypatch.chdir(tmp_path)

    # Monkeypatch preprocess_text to handle None gracefully
    def safe_preprocess(text):
        if text is None or not isinstance(text, str):
            return ""
        return text.upper()

    monkeypatch.setattr(ppr, "preprocess_text", safe_preprocess)

    # Run the function
    ppr.data_preprocessor(filename)

    # Check that the expected output file was created
    output_file = output_dir / f"tokenized_{filename}"
    assert output_file.exists(), f"Expected output file not found: {output_file}"

    # Verify the output CSV contents
    df_out = pd.read_csv(output_file)

    # Confirm that the tokenized_description column exists
    assert "tokenized_description" in df_out.columns

    # The first row should be uppercase, the second should be the title (filled for empty description)
    assert df_out["tokenized_description"].iloc[0] == "THIS IS A PROJECT"
    # The empty description should have been replaced by the title ("Book 2") and then tokenized.
    assert df_out["tokenized_description"].iloc[1] == "BOOK 2"


def test_data_preprocessor_bad_data_format(tmp_path, monkeypatch):
    """Should raise an error if the CSV doesn't contain 'description' column."""
    input_dir = tmp_path / "data" / "project_CSVs"
    output_dir = tmp_path / "data" / "tokenized_CSVs"
    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    filename = "bad_format.csv"
    df = pd.DataFrame({"name": ["Missing description column"]})
    df.to_csv(input_dir / filename, index=False)

    monkeypatch.chdir(tmp_path)

    with pytest.raises(KeyError):
        ppr.data_preprocessor(filename)