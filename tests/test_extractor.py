# Placeholder for extractor testing script
# Test: Extractor output matches expected output for good data, bad data, null data

# test_extractor.py
import pytest
import pandas as pd
from pathlib import Path

from project_recommender.extractor import text_to_projects_df_from_string, text_to_projects_df


@pytest.fixture
def sample_text():
    return """Project Title: Project A
Description: This is a sample project that demonstrates parsing.

Project Title: Project B
Description: Another project with a longer description that might be truncated depending on max_words.
"""

def test_returns_dataframe(sample_text):
    df = text_to_projects_df_from_string(sample_text)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Title", "Description"]


def test_two_rows_parsed(sample_text):
    df = text_to_projects_df_from_string(sample_text)
    assert len(df) == 2
    assert df.loc[0, "Title"] == "Project A"
    assert "sample project" in df.loc[0, "Description"]


def test_max_words_truncates(sample_text):
    df = text_to_projects_df_from_string(sample_text, max_words=5)
    desc = df.loc[0, "Description"].split()
    assert len(desc) <= 5


def test_invalid_input_type():
    with pytest.raises(TypeError):
        text_to_projects_df_from_string(12345)  # not a string


def test_no_projects_found_raises():
    bad_text = "This file has no correct labels."
    with pytest.raises(ValueError):
        text_to_projects_df_from_string(bad_text)


def test_text_to_projects_df_reads_file(tmp_path):
    file_path = tmp_path / "projects.txt"
    text = """Project Title: Alpha
Description: Something about Alpha.

Project Title: Beta
Description: Description of Beta.
"""
    file_path.write_text(text, encoding="utf-8")

    df = text_to_projects_df(str(file_path))
    assert len(df) == 2
    assert set(df["Title"]) == {"Alpha", "Beta"}
