# extractor.py
import re
from typing import List, Dict
import pandas as pd

_PROJECT_DESC_RE = re.compile(
    r'Project\s*Description[:\-]?\s*(?P<desc>.*?)(?=(?:\n{2,}|\Z|\nProject\s|Project\sTitle:))',
    re.IGNORECASE | re.DOTALL
)

# find title between "Location" and the next standalone "R" (case-insensitive)
_TITLE_BETWEEN_LOCATION_R_RE = re.compile(
    r'Location\s*(?P<title>.*?)\s*\bR\b',
    re.IGNORECASE | re.DOTALL
)


def _clean_whitespace(s: str) -> str:
    return re.sub(r'\s+', ' ', s.strip())


def _extract_from_string(text: str, max_words: int = 100) -> List[Dict[str, str]]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    # normalize newlines
    text = re.sub(r'\r\n?', '\n', text)

    rows: List[Dict[str, str]] = []

    for m in _PROJECT_DESC_RE.finditer(text):
        desc_raw = m.group('desc').strip()
        # limit description length
        if max_words and max_words > 0:
            desc = " ".join(_clean_whitespace(desc_raw).split()[:max_words])
        else:
            desc = _clean_whitespace(desc_raw)

        # attempt to find the title between "Location" and "R" preceding this description
        # we search in the text up to the start of the description match
        start_index = m.start()
        search_region = text[:start_index]

        title = ""
        # try to find the last occurrence where Location...R is present before description
        # using a reversed search for robustness: find all matches then take the last one
        title_matches = list(_TITLE_BETWEEN_LOCATION_R_RE.finditer(search_region))
        if title_matches:
            last_match = title_matches[-1]
            title = _clean_whitespace(last_match.group('title'))
            # if title contains newlines or metadata lines, take the first non-empty line
            lines = [ln.strip() for ln in title.splitlines() if ln.strip()]
            if lines:
                title = lines[0]
        else:
            # fallback: use the paragraph immediately before the "Project Description" block
            # split by double newlines and take the last paragraph before the description
            paras = [p.strip() for p in re.split(r'\n{2,}', search_region) if p.strip()]
            if paras:
                candidate = paras[-1]
                # take first line as title candidate
                title = _clean_whitespace(candidate.splitlines()[0])

        if not title:
            # final fallback: short snippet from description
            title = " ".join(_clean_whitespace(desc).split()[:8])

        rows.append({"Title": title, "Description": desc})

    if not rows:
        raise ValueError("No projects found using the simplified extractor patterns.")

    return rows


def text_to_projects_df_from_string(text: str, max_words: int = 100) -> pd.DataFrame:
    rows = _extract_from_string(text, max_words=max_words)
    return pd.DataFrame(rows, columns=["Title", "Description"])


def text_to_projects_df(file_path: str, max_words: int = 100) -> pd.DataFrame:
    with open(file_path, "r", encoding="utf-8") as f:
        txt = f.read()
    return text_to_projects_df_from_string(txt, max_words=max_words)


if __name__ == "__main__":
    # tiny self-test when run directly (adjust path as needed)
    try:
        df = text_to_projects_df("data/Rules of Life Projects Booklet v2 medium.txt", max_words=20000)
        print(df.to_string(index=False))
        print(df)
    except Exception as e:
        print("Extractor run error:", e)
