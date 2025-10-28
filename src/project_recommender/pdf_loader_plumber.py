import pdfplumber
import pandas as pd
import re
from pathlib import Path

"""
from pdf_loader_plumber import ...()
pdf_plumber(filepath="")
"""
pdf_path = "data/booklet_full.pdf"
output_path = Path("data/projects_summary.csv")

# Labels we care about (lowercased, spaces collapsed)
LABEL_TITLE = "project no & title"
LABEL_SUPERVISORS = "supervisors"
LABEL_DESCRIPTION = "project description"
STOP_DESCRIPTION_LABELS = {"reasonable expected outcome", "reasonab"}  # things that signal end of description

def normalize(s):
    if s is None:
        return ""
    # collapse whitespace and unify newlines -> space
    return re.sub(r"\s+", " ", str(s)).strip()

def is_label_cell(text, target):
    """Return True if text looks like the label `target`. Handles split words."""
    if not text:
        return False
    t = normalize(text).lower()
    # Direct substring match is robust to splits like "Project No & Title" or "Project No &\nTitle"
    return target in t

def extract_projects_from_table(table_rows):
    """
    table_rows: list of rows, where each row is list of raw cells (may include None)
    returns: list of dicts with keys: Title, Supervisors, Project Description
    """
    projects = []
    cur = {"Project Title": "", "Supervisors": "", "Project Description": ""}
    collecting_desc = False

    i = 0
    while i < len(table_rows):
        row = table_rows[i]
        # normalize entire row cells
        cells = [normalize(c) for c in row]
        # find first non-empty cell index for better heuristics
        first_non_empty_idx = next((j for j, c in enumerate(cells) if c), None)

        first_cell = cells[first_non_empty_idx] if first_non_empty_idx is not None else ""

        # Detect title label
        if is_label_cell(first_cell, LABEL_TITLE):
            # If we already have a project with a title, store it and start new
            if cur["Project Title"]:
                projects.append(cur)
                cur = {"Project Title": "", "Supervisors": "", "Project Description": ""}
                collecting_desc = False

            # Prefer the same row's remaining cells as the title
            if any(cells[j] for j in range(first_non_empty_idx + 1, len(cells))):
                title = " ".join([cells[j] for j in range(first_non_empty_idx + 1, len(cells)) if cells[j]])
                cur["Project Title"] = title
            else:
                # fallback: look at the next row(s) for the actual title text
                # join subsequent non-empty cells from next row until we hit an obvious label
                j = i + 1
                title_parts = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    # stop if next row looks like another label (supervisors, remit, etc.)
                    if any(is_label_cell(c, LABEL_SUPERVISORS) or is_label_cell(c, LABEL_DESCRIPTION) or is_label_cell(c, "remit") for c in next_cells if c):
                        break
                    title_parts.extend([c for c in next_cells if c])
                    j += 1
                cur["Project Title"] = " ".join(title_parts).strip()

        # Detect supervisors label
        elif is_label_cell(first_cell, LABEL_SUPERVISORS):
            # Supervisor names may be in same row after label or in following cell(s)
            if any(cells[j] for j in range(first_non_empty_idx + 1, len(cells))):
                cur["Supervisors"] = " ".join([cells[j] for j in range(first_non_empty_idx + 1, len(cells)) if cells[j]])
            else:
                # gather from following rows until next label
                j = i + 1
                sup_parts = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(is_label_cell(c, LABEL_DESCRIPTION) or is_label_cell(c, LABEL_TITLE) or is_label_cell(c, "remit") for c in next_cells if c):
                        break
                    sup_parts.extend([c for c in next_cells if c])
                    j += 1
                cur["Supervisors"] = " ".join(sup_parts).strip()

        # Detect project description start
        elif is_label_cell(first_cell, LABEL_DESCRIPTION):
            # Start collecting description text from this row's non-label cells (if any) and subsequent rows
            collecting_desc = True
            desc_parts = []
            # may be content in same row after label
            if any(cells[j] for j in range(first_non_empty_idx + 1, len(cells))):
                desc_parts.append(" ".join([cells[j] for j in range(first_non_empty_idx + 1, len(cells)) if cells[j]]))
            # gather following rows until a stop label appears
            j = i + 1
            while j < len(table_rows):
                next_cells = [normalize(x) for x in table_rows[j]]
                # if any cell looks like a stop label, break
                if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                    break
                # otherwise append the whole row's text
                row_text = " ".join([c for c in next_cells if c])
                if row_text:
                    desc_parts.append(row_text)
                j += 1
            cur["Project Description"] = " ".join(desc_parts).strip()
            # skip forward to j-1 because outer loop will increment i
            i = j - 1
            collecting_desc = False

        # Some PDFs place the label in column 0 and the value in column 1, so also check column 1 for labels
        else:
            # if first cell is empty, check second cell for labels
            second_cell = cells[1] if len(cells) > 1 else ""
            if is_label_cell(second_cell, LABEL_TITLE):
                # treat second cell as label; title maybe in later columns
                if any(cells[j] for j in range(2, len(cells))):
                    cur["Project Title"] = " ".join([cells[j] for j in range(2, len(cells)) if cells[j]])
            elif is_label_cell(second_cell, LABEL_SUPERVISORS):
                if any(cells[j] for j in range(2, len(cells))):
                    cur["Supervisors"] = " ".join([cells[j] for j in range(2, len(cells)) if cells[j]])
            elif is_label_cell(second_cell, LABEL_DESCRIPTION):
                # collect description from column 2 onwards, plus following rows
                desc_parts = []
                if any(cells[j] for j in range(2, len(cells))):
                    desc_parts.append(" ".join([cells[j] for j in range(2, len(cells)) if cells[j]]))
                j = i + 1
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                        break
                    row_text = " ".join([c for c in next_cells if c])
                    if row_text:
                        desc_parts.append(row_text)
                    j += 1
                cur["Project Description"] = " ".join(desc_parts).strip()
                i = j - 1

        i += 1

    # final project append
    if cur["Project Title"] or cur["Supervisors"] or cur["Project Description"]:
        projects.append(cur)
    return projects

def parse_pdf(pdf_path):
    all_projects = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # try both extract_table (single) and extract_tables (multiple)
            tables = []
            t = page.extract_table()
            if t:
                tables.append(t)
            try:
                more = page.extract_tables()
                if more:
                    for mt in more:
                        if mt not in tables:
                            tables.append(mt)
            except Exception:
                pass

            for table in tables:
                # ensure table rows are lists and normalize None -> ""
                rows = [[(cell if cell is not None else "") for cell in row] for row in table]
                projects = extract_projects_from_table(rows)
                all_projects.extend(projects)

    # deduplicate / clean whitespace
    for p in all_projects:
        for k, v in p.items():
            p[k] = normalize(v)

    return all_projects

if __name__ == "__main__":
    projects = parse_pdf(pdf_path)
    if not projects:
        print("No projects found.")
    else:
        df = pd.DataFrame(projects)
        # keep only the columns we want and give nice headers
        df = df[["title", "supervisors", "project description"]]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✅ Wrote {len(df)} project(s) to: {output_path.resolve()}")
        print(df.head())
