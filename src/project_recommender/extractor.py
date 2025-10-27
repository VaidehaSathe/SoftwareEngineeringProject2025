import re
import pandas as pd

"""
This file takes a .txt file in the format like:

Project Title: Project 1
Description: This is a project that takes ...

Project Title: Project 2
Description: Another project...

and turns it into a df object of the form:

    Title      Description
0   Project A  This is a project that takes ...
1   Project B  Another project ...

"""

def text_to_projects_df(file_path: str, max_words: int = 100) -> pd.DataFrame:
    """Parse a text file with 'Project Title:' and 'Description:' entries into a DataFrame."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalize spacing
    text = re.sub(r'\r\n?', '\n', text)

    # Find all project blocks
    pattern = re.compile(
        r'Project\s*Title:\s*(?P<title>.*?)\n\s*Description:\s*(?P<desc>.*?)(?=\n\s*Project\s*Title:|$)',
        re.DOTALL | re.IGNORECASE
    )
    matches = pattern.findall(text)

    rows = []
    for title, desc in matches:
        # Clean and truncate description
        desc = re.sub(r'\s+', ' ', desc.strip())
        desc = " ".join(desc.split()[:max_words])
        rows.append({"Title": title.strip(), "Description": desc})

    if not rows:
        raise ValueError("No projects found. Check that your file uses 'Project Title:' and 'Description:' labels.")

    return pd.DataFrame(rows)

# Example usage
if __name__ == "__main__":
    df = text_to_projects_df("data/data.txt")
    print(df)
