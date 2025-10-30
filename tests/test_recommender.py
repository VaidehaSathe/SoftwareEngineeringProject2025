import pandas as pd
import pytest
from pathlib import Path

MODULE = "src.project_recommender.recommender"

try:
    recommender = __import__(MODULE, fromlist=["*"])
except Exception as e:
    raise ImportError(
        f"Could not import module {MODULE!r}. Adjust MODULE at top of this test file to "
        "match your module import path (e.g. 'projects_recommend.recommender').\n"
        f"Original import error: {e!r}"
    )

# Fixture for a sample tokenized CSV
@pytest.fixture
def simple_csv(tmp_path):
    """Create a simple tokenized CSV with required columns and return its path."""
    df = pd.DataFrame({
        "title": ["Project A", "Project B"],
        # tokenized_description should be pre-processed text used by TfidfVectorizer
        "tokenized_description": ["covid pandemic study", "machine learning bioinformatics"],
        "primary_theme": ["Epidemiology", "AI"],
        "supervisors": ["Dr A", "Dr B"]
    })
    p = tmp_path / "tokenized.csv"
    df.to_csv(p, index=False)
    return p

# Tests for recommend()
def test_recommend_returns_dataframe_for_good_input(monkeypatch, simple_csv):
    """
    Good input:
     - long user input (>15 words)
     - valid tokenized csv path
     - query_preprocessor returns a tokenized string matching file content
    Expect:
     - DataFrame returned
     - at least one recommendation and 'score' column present
    """
    # make user input > 15 words
    user_input = "I am a researcher who is very interested in studying the pandemic and its societal effects on health outcomes"  # >15 words

    # monkeypatch query_preprocessor inside module to return tokens that will match Project A
    monkeypatch.setattr(recommender, "query_preprocessor", lambda s: "covid pandemic study")

    df = recommender.recommend(user_input, str(simple_csv), amount_wanted=1)
    # should return a pandas DataFrame
    assert isinstance(df, pd.DataFrame)
    assert "title" in df.columns
    assert "score" in df.columns
    assert len(df) >= 1
    assert df.iloc[0]["title"] in {"Project A", "Project B"}


def test_recommend_short_input_returns_message(monkeypatch, simple_csv):
    """
    If user input <= 15 words, function returns the "too short" message string.
    """
    short_input = "Too short statement"
    # ensure preprocessor won't interfere
    monkeypatch.setattr(recommender, "query_preprocessor", lambda s: "irrelevant")
    result = recommender.recommend(short_input, str(simple_csv), amount_wanted=1)
    assert isinstance(result, str)
    assert "too short" in result.lower()


def test_recommend_missing_csv_columns_raises(monkeypatch, tmp_path):
    """
    If the CSV lacks required columns (e.g. 'tokenized_description'), ensure a KeyError is raised.
    """
    df = pd.DataFrame({
        "title": ["X"],
        "primary_theme": ["T"],
        "supervisors": ["S"]
        # tokenized_description intentionally missing
    })
    p = tmp_path / "bad.csv"
    df.to_csv(p, index=False)

    long_input = " ".join(["word"] * 20)
    monkeypatch.setattr(recommender, "query_preprocessor", lambda s: "word")

    with pytest.raises(KeyError):
        recommender.recommend(long_input, str(p), amount_wanted=1)


def test_recommend_null_user_input_raises(monkeypatch, simple_csv):
    """
    If user_input is None, .split() will fail — assert that a TypeError or AttributeError is raised.
    """
    monkeypatch.setattr(recommender, "query_preprocessor", lambda s: "foo")
    with pytest.raises(Exception) as exc:
        recommender.recommend(None, str(simple_csv), amount_wanted=1)
    # Accept AttributeError/TypeError as valid failure modes for None input
    assert isinstance(exc.value, (AttributeError, TypeError))


# Tests for resolve_data_path
def test_resolve_data_path_with_absolute_path(tmp_path):
    """
    If an absolute path is provided, resolve_data_path should return it (resolved).
    """
    f = tmp_path / "afile.csv"
    f.write_text("dummy")
    resolved = recommender.resolve_data_path(str(f))
    assert isinstance(resolved, Path)
    # resolved should point to the same file
    assert resolved == f.resolve()


def test_resolve_data_path_with_cwd_candidate(tmp_path, monkeypatch):
    """
    If the path exists relative to CWD, that should be chosen.
    """
    # Create a file in tmp_path and chdir there
    monkeypatch.chdir(tmp_path)
    rel = Path("local.csv")
    rel.write_text("x")
    resolved = recommender.resolve_data_path(str(rel))
    assert resolved == (Path.cwd() / rel).resolve()


def test_resolve_data_path_project_root_candidate(tmp_path, monkeypatch):
    """
    Ensure that resolve_data_path will find a file located under PROJECT_ROOT / <given_path>.
    This uses the module's PROJECT_ROOT variable to place a candidate file.
    """
    project_root = getattr(recommender, "PROJECT_ROOT", None)
    if project_root is None:
        pytest.skip("Module under test does not expose PROJECT_ROOT; skipping this test.")

    # create candidate relative to PROJECT_ROOT
    candidate = Path(project_root) / "some_rel_path.csv"
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text("ok")
    resolved = recommender.resolve_data_path(str(Path("some_rel_path.csv")))
    assert resolved == candidate.resolve()


def test_resolve_data_path_raises_if_not_found(tmp_path):
    """
    If file cannot be found by any strategy, resolve_data_path must raise FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        recommender.resolve_data_path("definitely_not_a_real_file_12345.csv")
