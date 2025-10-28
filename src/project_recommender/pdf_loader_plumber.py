# pdf_loader_plumber.py

# Date: 28/10/2025 
#--------------------------------------------------------#
# Description: This is a updated PDF -> raw text script that uses pdfplumber
# Functionality: PDF (filepath) --> csv file with columns [title, supervisors, project description]
# 
# To run, cd into project_recommender, and then do: python pdf_loader_plumber.py [filepath]
# It will output project_summary.csv under the data folder next to src. 

# THIS MODULE CAN BE CALLED FROM OUTSIDE
# e.g. from main.py or cli.py: 
# from src.project_recommender.pdf_loader_plumber import process_pdf_to_csv, parse_pdf

# # Example 1: Parse and save CSV
# csv_path = process_pdf_to_csv("data/booklet_full.pdf")
# print(f"✅ CSV saved at: {csv_path}")

# # Example 2: Just get project data as a list of dicts
# projects = parse_pdf("data/booklet_full.pdf")
# for p in projects[:3]:
#     print(p["title"], "-", p["supervisors"])
#--------------------------------------------------------#

# pdf_loader_plumber.py
from pathlib import Path
import re
from typing import List, Dict, Optional, Union
import pdfplumber
import pandas as pd
import logging

# --- logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- labels / config ---
LABEL_TITLE = "project no & title"
LABEL_SUPERVISORS = "supervisors"
LABEL_DESCRIPTION = "project description"
STOP_DESCRIPTION_LABELS = {"reasonable expected outcome", "reasonab"}  # signals end of description

# --- repo root detection ---
def find_repo_root(start: Optional[Union[str, Path]] = None) -> Path:
    """
    Walk upward from start and return the first directory that contains either:
      - a .git directory (preferred)
      - or a src/ directory
    If none found, fall back to the start's grandparent if available, otherwise cwd.
    """
    if start is None:
        # Prefer __file__ location if available, else cwd
        try:
            start_path = Path(__file__).resolve()
        except Exception:
            start_path = Path.cwd()
    else:
        start_path = Path(start)

    # if start is a file, move to its parent
    if start_path.is_file():
        current = start_path.parent
    else:
        current = start_path

    # walk up to filesystem root
    root = current.anchor or Path(current).resolve().anchor
    while True:
        # check for .git first (preferred)
        if (current / ".git").exists():
            return current
        # then check for src directory
        if (current / "src").is_dir():
            return current
        # stop if reached root
        if current.parent == current:
            break
        current = current.parent

    # fallback heuristics: try two parents above __file__ (common layout)
    try:
        fallback = Path(__file__).resolve().parents[2]
        if fallback.exists():
            return fallback
    except Exception:
        pass

    # final fallback: current working directory
    return Path.cwd()

# compute repo root & defaults at import-time
try:
    REPO_ROOT = find_repo_root()
except Exception:
    REPO_ROOT = Path.cwd()

DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_CSV = DEFAULT_DATA_DIR / "projects_summary.csv"
logger.debug("Repo root resolved to: %s", REPO_ROOT)

# --- helpers ---
def normalize(s: Optional[str]) -> str:
    """Collapse whitespace and return a cleaned string (safe for None)."""
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()

def is_label_cell(text: Optional[str], target: str) -> bool:
    """Return True if text looks like the label `target`. Handles split words."""
    if not text:
        return False
    t = normalize(text).lower()
    return target in t

# --- extraction logic ---
def extract_projects_from_table(table_rows: List[List[Optional[str]]]) -> List[Dict[str, str]]:
    """
    table_rows: list of rows, where each row is list of raw cells (may include None)
    returns: list of dicts with keys: title, supervisors, description
    """
    projects: List[Dict[str, str]] = []
    cur = {"title": "", "supervisors": "", "description": ""}
    collecting_desc = False

    i = 0
    while i < len(table_rows):
        row = table_rows[i]
        # normalize entire row cells
        cells = [normalize(c) for c in row]
        first_non_empty_idx = next((j for j, c in enumerate(cells) if c), None)
        first_cell = cells[first_non_empty_idx] if first_non_empty_idx is not None else ""

        # Detect title label
        if is_label_cell(first_cell, LABEL_TITLE):
            if cur["title"]:
                projects.append(cur)
                cur = {"title": "", "supervisors": "", "description": ""}
                collecting_desc = False

            # Prefer same row remainder as title
            if any(cells[j] for j in range(first_non_empty_idx + 1, len(cells))):
                title = " ".join([cells[j] for j in range(first_non_empty_idx + 1, len(cells)) if cells[j]])
                cur["title"] = title
            else:
                j = i + 1
                title_parts: List[str] = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(is_label_cell(c, LABEL_SUPERVISORS) or is_label_cell(c, LABEL_DESCRIPTION) or is_label_cell(c, "remit") for c in next_cells if c):
                        break
                    title_parts.extend([c for c in next_cells if c])
                    j += 1
                cur["title"] = " ".join(title_parts).strip()

        # Detect supervisors label
        elif is_label_cell(first_cell, LABEL_SUPERVISORS):
            if any(cells[j] for j in range(first_non_empty_idx + 1, len(cells))):
                cur["supervisors"] = " ".join([cells[j] for j in range(first_non_empty_idx + 1, len(cells)) if cells[j]])
            else:
                j = i + 1
                sup_parts: List[str] = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(is_label_cell(c, LABEL_DESCRIPTION) or is_label_cell(c, LABEL_TITLE) or is_label_cell(c, "remit") for c in next_cells if c):
                        break
                    sup_parts.extend([c for c in next_cells if c])
                    j += 1
                cur["supervisors"] = " ".join(sup_parts).strip()

        # Detect project description start
        elif is_label_cell(first_cell, LABEL_DESCRIPTION):
            collecting_desc = True
            desc_parts: List[str] = []
            if any(cells[j] for j in range(first_non_empty_idx + 1, len(cells))):
                desc_parts.append(" ".join([cells[j] for j in range(first_non_empty_idx + 1, len(cells)) if cells[j]]))
            j = i + 1
            while j < len(table_rows):
                next_cells = [normalize(x) for x in table_rows[j]]
                if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                    break
                row_text = " ".join([c for c in next_cells if c])
                if row_text:
                    desc_parts.append(row_text)
                j += 1
            cur["description"] = " ".join(desc_parts).strip()
            i = j - 1
            collecting_desc = False

        else:
            # Also check second column for labels (some PDFs use column 1 as label)
            second_cell = cells[1] if len(cells) > 1 else ""
            if is_label_cell(second_cell, LABEL_TITLE):
                if any(cells[j] for j in range(2, len(cells))):
                    cur["title"] = " ".join([cells[j] for j in range(2, len(cells)) if cells[j]])
            elif is_label_cell(second_cell, LABEL_SUPERVISORS):
                if any(cells[j] for j in range(2, len(cells))):
                    cur["supervisors"] = " ".join([cells[j] for j in range(2, len(cells)) if cells[j]])
            elif is_label_cell(second_cell, LABEL_DESCRIPTION):
                desc_parts: List[str] = []
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
                cur["description"] = " ".join(desc_parts).strip()
                i = j - 1

        i += 1

    # append final
    if cur["title"] or cur["supervisors"] or cur["description"]:
        projects.append(cur)
    return projects

# --- parsing function (importable) ---
def parse_pdf(pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
    """
    Parse a PDF file and return a list of project dicts:
      [{"title": "...", "supervisors": "...", "description": "..."}, ...]
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    all_projects: List[Dict[str, str]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables: List[List[List[Optional[str]]]] = []
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
                # some pages/tables can trigger odd errors; skip safely
                logger.debug("Ignored extract_tables() exception on a page.", exc_info=False)
                pass

            for table in tables:
                # ensure table rows are lists and normalize None -> ""
                rows = [[(cell if cell is not None else "") for cell in row] for row in table]
                projects = extract_projects_from_table(rows)
                all_projects.extend(projects)

    # normalize whitespace
    for p in all_projects:
        for k, v in list(p.items()):
            p[k] = normalize(v)

    return all_projects

# --- convenience: process and save to csv (importable) ---
def process_pdf_to_csv(pdf_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Parse given pdf_path and write projects to CSV. Returns Path of the written file.
    If output_path is omitted, writes to <repo_root>/data/projects_summary.csv
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # choose default output in repo_root/data unless caller provided a path
    if output_path is None:
        output_path = DEFAULT_CSV
    output_path = Path(output_path)

    # ensure parent directory exists (and log where we're writing)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Writing CSV to: %s", output_path.resolve())

    projects = parse_pdf(pdf_path)

    if not projects:
        df = pd.DataFrame(columns=["title", "supervisors", "description"])
        df.to_csv(output_path, index=False)
        logger.info("No projects found; wrote CSV with headers only.")
    else:
        df = pd.DataFrame(projects)
        # ensure consistent column order (if keys missing, create empty)
        for col in ["title", "supervisors", "description"]:
            if col not in df.columns:
                df[col] = ""
        df = df[["title", "supervisors", "description"]]
        df.to_csv(output_path, index=False)
        logger.info("Wrote %d project(s).", len(df))

    return output_path.resolve()

# --- CLI entrypoint ---
def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Extract projects from a PDF into a CSV (using pdfplumber).")
    parser.add_argument("pdf", help="path to PDF file to parse")
    parser.add_argument("-o", "--output", help="path to output CSV (default: repository-root data/projects_summary.csv)", default=None)
    args = parser.parse_args()

    # if output not provided, show the default that will be used
    if args.output is None:
        logger.info("No output path supplied; using default CSV: %s", DEFAULT_CSV.resolve())
    else:
        logger.info("Using supplied output path: %s", Path(args.output).resolve())

    try:
        outpath = process_pdf_to_csv(args.pdf, args.output)
    except Exception as exc:
        logger.error("Failed to process PDF: %s", exc)
        raise SystemExit(1)

    logger.info("Finished. CSV at: %s", outpath)

# allow calling as script
if __name__ == "__main__":
    _cli()

# explicit exports
__all__ = ["parse_pdf", "process_pdf_to_csv", "extract_projects_from_table", "normalize", "is_label_cell", "find_repo_root"]
