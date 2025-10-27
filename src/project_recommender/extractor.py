# Placeholder for extractor script
# Functionality: (Data) text -> (Data) CSV

import re
import pandas as pd
from typing import List

def _first_nonempty_line(lines: List[str]) -> str:
    for ln in lines:
        s = ln.strip(" -•\t")
        if s:
            return s
    return ""

def _take_first_n_words(text: str, n: int) -> str:
    words = text.split()
    return " ".join(words[:n])

def text_to_projects_df(raw_text: str,
                        desc_marker: str = "Project Description:",
                        max_words: int = 100) -> pd.DataFrame:
    """
    Parse PDF-extracted raw_text into a DataFrame with columns 'Title' and 'Description'.
    - Looks for blocks separated by two or more newlines.
    - Each block that contains desc_marker is considered a project.
    - Title is taken as the line immediately before the marker if present,
      otherwise the first non-empty line of the block.
    - Description is the text after desc_marker, whitespace-normalized, truncated to max_words.
    """
    # Normalize newlines (some PDFs use \r\n, etc.)
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Split into blocks on 2+ newlines (common separation in PDF->text)
    blocks = [b.strip() for b in re.split(r'\n{2,}', text) if b.strip()]

    rows = []
    for b in blocks:
        if desc_marker not in b:
            continue

        # Split block into lines for title heuristics
        lines = [ln for ln in b.splitlines()]

        # Try to get the title as the line immediately before the marker
        # If marker appears multiple times, handle each occurrence.
        for match in re.finditer(re.escape(desc_marker), b):
            # Determine the substring up to the marker position
            pre = b[: match.start() ]
            post = b[ match.end() : ]

            # Find last non-empty line in 'pre' as title candidate
            pre_lines = [ln.strip(" -•\t") for ln in pre.splitlines() if ln.strip()]
            title_candidate = pre_lines[-1] if pre_lines else None

            # Fallback: use the block's first non-empty line
            if not title_candidate:
                title_candidate = _first_nonempty_line(lines)

            # Clean and prepare description: collapse whitespace, take first max_words
            descr_raw = re.sub(r'\s+', ' ', post.strip())
            descr_short = _take_first_n_words(descr_raw, max_words)

            if title_candidate and descr_short:
                rows.append({"Title": title_candidate, "Description": descr_short})
            # if either missing, skip this occurrence

    if not rows:
        raise ValueError(
            "Parsed zero projects. Make sure your PDF text contains the marker "
            f"'{desc_marker}' and that splitting on blank lines is appropriate."
        )

    df = (
        pd.DataFrame(rows)
        .drop_duplicates(subset=["Title"])
        .reset_index(drop=True)
    )
    return df

# ---------------------
# Example quick test
# ---------------------
if __name__ == "__main__":
    sample = """
    Amazing Project A
    Project Description:
    This project explores the application of X in Y. It does many things.
    More detail and extra lines that should be collapsed.

    Some other heading

    Project B
    Project Description:
    An independent project. It has a long description that will be cut to the first one hundred words.
    """
    df = text_to_projects_df(sample)
    print(df)
