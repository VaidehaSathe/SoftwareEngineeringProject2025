# extractor.py
import re
import pandas as pd
from typing import List

"""
This file parses project listings in this format:

Project Title: Project 1
Description: This is a project that takes ...

Project Title: Project 2
Description: Another project...

It exposes a function that accepts a text string, and a backwards-compatible
function that reads from a .txt file path.
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
        max_words: maximum words to keep for description (truncate longer descriptions)

    Returns:
        pd.DataFrame with columns ["Title", "Description"]
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
        rows.append({"Title": title.strip(), "Description": desc})

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
