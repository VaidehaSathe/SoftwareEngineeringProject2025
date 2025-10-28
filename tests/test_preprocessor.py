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
    # Create fake folder structure
    input_dir = tmp_path / "data" / "project_CSVs"
    output_dir = tmp_path / "data" / "tokenized_CSVs"
    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    # Create dummy CSV
    filename = "projects.csv"
    input_file = input_dir / filename
    df = pd.DataFrame({
        "title": ["Book 1", "Book 2"],
        "description": ["This is the first project", "Second project description"]
    })
    df.to_csv(input_file, index=False)

    # Monkeypatch working directory
    monkeypatch.chdir(tmp_path)

    # Patch preprocess_text for predictability
    monkeypatch.setattr(ppr, "preprocess_text", lambda s: s.upper())

    # Run the function
    ppr.data_preprocessor(filename)

    # Verify output file created
    output_file = output_dir / filename
    assert output_file.exists()

    # Verify contents
    result = pd.read_csv(output_file)
    assert "tokenized_description" in result.columns
    assert result["tokenized_description"].iloc[0] == "THIS IS THE FIRST PROJECT"


def test_data_preprocessor_missing_file(tmp_path, monkeypatch):
    """Should raise FileNotFoundError if input CSV doesn't exist."""
    base = tmp_path / "data"
    (base / "project_CSVs").mkdir(parents=True)
    (base / "tokenized_CSVs").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        ppr.data_preprocessor("nonexistent.csv")


def test_data_preprocessor_null_description(tmp_path, monkeypatch):
    """Should handle null or NaN in description column gracefully."""
    input_dir = tmp_path / "data" / "project_CSVs"
    output_dir = tmp_path / "data" / "tokenized_CSVs"
    input_dir.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    filename = "null_test.csv"
    df = pd.DataFrame({
        "title": ["Project 1", "Project 2"],
        "description": ["Good description", None]
    })
    df.to_csv(input_dir / filename, index=False)

    monkeypatch.chdir(tmp_path)

    # Patch preprocess_text to handle None safely
    def safe_preprocess(text):
        if text is None or not isinstance(text, str):
            return ""
        return text.upper()

    monkeypatch.setattr(ppr, "preprocess_text", safe_preprocess)

    ppr.data_preprocessor(filename)

    # Check results
    result = pd.read_csv(output_dir / filename)
    assert result["tokenized_description"].fillna("").iloc[1] == ""


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