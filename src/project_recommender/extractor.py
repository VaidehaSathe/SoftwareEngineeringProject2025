# This file is OBSOLETE - raw text parsing and extraction is done solely by pdf_loader_plumber
# Date: 27/10/2025 
#--------------------------------------------------------#
# Description: This module contains takes a string or .txt file as a input and returns a dataframe object.
# Functionality: Raw text from a PDF --> pandas df with columns (title, description)
# text_to_projects_df_from_string: takes 100 words of a string input (the description of the project)
# text_to_projects_df: same as above, but takes a .txt input
#--------------------------------------------------------#

import re
import pandas as pd
from typing import List


"""
This block defines a regex pattern that the extracor uses to find pairs of "Project Titles"
and "Descriptions".

This will scan through all lines in text and gives two groups by matching literal words: 
title (the text after "Project Title"S); and desc (the text after "Description"). 
"""
_PROJECT_BLOCK_RE = re.compile(
    r'Project\s*Title:\s*(?P<title>.*?)\n\s*Description:\s*(?P<desc>.*?)(?=\n\s*Project\s*Title:|$)',
    re.DOTALL | re.IGNORECASE
    
)

def text_to_projects_df_from_string(text: str, max_words: int = 100) -> pd.DataFrame:
    """
    Parse a text string with 'Project Title:' and 'Description:' entries into a DataFrame.

    Args:
        text: full text containing one or more Project Title / Description blocks
        max_words: maximum words to keep for description (arbitrary cutoff of long descriptions)

    Returns:
        pd.DataFrame with columns ["title", "description"]
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    # Normalize line endings
    text = re.sub(r'\r\n?', '\n', text)

    matches = _PROJECT_BLOCK_RE.findall(text)
    rows: List[dict] = []
    for title, desc in matches:
        desc = re.sub(r'\s+', ' ', desc.strip())
        if max_words is not None and max_words > 0:
            desc = " ".join(desc.split()[:max_words])
        rows.append({"title": title.strip(), "description": desc})

    if not rows:
        raise ValueError("No projects found. Check that your text uses 'Project Title:' and 'Description:' labels.")

    return pd.DataFrame(rows)


def text_to_projects_df(file_path: str, max_words: int = 100) -> pd.DataFrame:
    """
    Backwards-compatible helper: read a file and parse it.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return text_to_projects_df_from_string(text, max_words=max_words)


if __name__ == "__main__":
    # quick manual test
    sample = """Project Title: Project A
Description: This is a sample project that demonstrates parsing.

Project Title: Project B
Description: Another project with a longer description that might be truncated depending on max_words.
"""
    df = text_to_projects_df_from_string(sample, max_words=20)
    print(df)
