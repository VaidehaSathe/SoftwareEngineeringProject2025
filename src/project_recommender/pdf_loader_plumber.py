# pdf_loader_plumber.py
# Date: 28/10/2025
"""
PDF -> CSV (pdfplumber)
Reads PDFs from:  data/raw_PDFs/
Writes CSVs to:   data/project_CSVs/ [title,primary_theme,supervisors,description]

Usage:
  # Process all PDFs in data/raw_PDFs and write single CSV:
  python src/project_recommender/pdf_loader_plumber.py

  # Process a single PDF (filename looked for in data/raw_PDFs if not given as a path)
  python src/project_recommender/pdf_loader_plumber.py somefile.pdf

  # Specify explicit output file
  python src/project_recommender/pdf_loader_plumber.py -o data/project_CSVs/my_projects.csv
"""
from pathlib import Path
import re
from typing import List, Dict, Optional, Union
import pdfplumber
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- labels / config ---
LABEL_TITLE = "project no & title"
LABEL_SUPERVISORS = "supervisors"
LABEL_DESCRIPTION = "project description"
LABEL_PRIMARY_THEME = "primary theme"
# additional label tokens that indicate boundaries when accumulating multi-row fields
BOUNDARY_LABELS = {LABEL_SUPERVISORS, LABEL_DESCRIPTION, LABEL_PRIMARY_THEME, "remit"}
STOP_DESCRIPTION_LABELS = {"reasonable expected outcome", "reasonab"}

# --- repo / data dirs ---
def repo_root_guess() -> Path:
    try:
        return Path(__file__).resolve().parents[2]
    except Exception:
        return Path.cwd()

REPO_ROOT = repo_root_guess()
RAW_PDF_DIR = (REPO_ROOT / "data" / "raw_PDFs").resolve()
CSV_OUTPUT_DIR = (REPO_ROOT / "data" / "project_CSVs").resolve()

RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_COMBINED_CSV = CSV_OUTPUT_DIR / "projects_summary.csv"

logger.debug("REPO_ROOT: %s", REPO_ROOT)
logger.debug("RAW_PDF_DIR: %s", RAW_PDF_DIR)
logger.debug("CSV_OUTPUT_DIR: %s", CSV_OUTPUT_DIR)

# --- helpers ---
def normalize(s: Optional[str]) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()

def is_label_cell(text: Optional[str], target: str) -> bool:
    if not text:
        return False
    return target in normalize(text).lower()

def looks_like_boundary(next_cells: List[str]) -> bool:
    """Return True if any of the next_cells contains a known boundary label."""
    for c in next_cells:
        if not c:
            continue
        low = normalize(c).lower()
        if any(lbl in low for lbl in BOUNDARY_LABELS):
            return True
    return False

# --- extraction (kept as your logic) ---
def extract_projects_from_table(table_rows: List[List[Optional[str]]]) -> List[Dict[str, str]]:
    projects: List[Dict[str, str]] = []
    cur = {"title": "", "primary_theme": "", "supervisors": "", "description": ""}
    i = 0
    while i < len(table_rows):
        cells = [normalize(c) for c in table_rows[i]]
        first_non_empty_idx = next((j for j, c in enumerate(cells) if c), None)
        first_cell = cells[first_non_empty_idx] if first_non_empty_idx is not None else ""

        # TITLE
        if is_label_cell(first_cell, LABEL_TITLE):
            # push previous if any
            if cur["title"] or cur["primary_theme"] or cur["supervisors"] or cur["description"]:
                projects.append(cur)
                cur = {"title": "", "primary_theme": "", "supervisors": "", "description": ""}

            # attempt to take the rest of the same row as title
            rest = " ".join(cells[first_non_empty_idx + 1 :]).strip()
            if rest:
                cur["title"] = rest
            else:
                # accumulate title from subsequent rows until we hit another label
                j = i + 1
                parts = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if looks_like_boundary(next_cells):
                        break
                    parts.extend([c for c in next_cells if c])
                    j += 1
                cur["title"] = " ".join(parts).strip()

        # PRIMARY THEME
        elif is_label_cell(first_cell, LABEL_PRIMARY_THEME):
            rest = " ".join(cells[first_non_empty_idx + 1 :]).strip()
            if rest:
                cur["primary_theme"] = rest
            else:
                j = i + 1
                parts = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    # theme likely short; stop if we hit other labels
                    if looks_like_boundary(next_cells):
                        break
                    parts.extend([c for c in next_cells if c])
                    j += 1
                cur["primary_theme"] = " ".join(parts).strip()

        # SUPERVISORS
        elif is_label_cell(first_cell, LABEL_SUPERVISORS):
            rest = " ".join(cells[first_non_empty_idx + 1 :]).strip()
            if rest:
                cur["supervisors"] = rest
            else:
                j = i + 1
                parts = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(is_label_cell(c, LABEL_DESCRIPTION) or is_label_cell(c, LABEL_TITLE) or is_label_cell(c, LABEL_PRIMARY_THEME) for c in next_cells if c):
                        break
                    parts.extend([c for c in next_cells if c])
                    j += 1
                cur["supervisors"] = " ".join(parts).strip()

        # DESCRIPTION
        elif is_label_cell(first_cell, LABEL_DESCRIPTION):
            parts = []
            rest = " ".join(cells[first_non_empty_idx + 1 :]).strip()
            if rest:
                parts.append(rest)
            j = i + 1
            while j < len(table_rows):
                next_cells = [normalize(x) for x in table_rows[j]]
                if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                    break
                # stop if we hit a boundary label (new field)
                if looks_like_boundary(next_cells):
                    break
                row_text = " ".join([c for c in next_cells if c]).strip()
                if row_text:
                    parts.append(row_text)
                j += 1
            cur["description"] = " ".join(parts).strip()
            i = j - 1

        else:
            # fallback: check second column for labels (some PDFs use column 1 as label)
            second = cells[1] if len(cells) > 1 else ""
            if is_label_cell(second, LABEL_TITLE):
                cur["title"] = " ".join(cells[2:]).strip()
            elif is_label_cell(second, LABEL_PRIMARY_THEME):
                cur["primary_theme"] = " ".join(cells[2:]).strip()
            elif is_label_cell(second, LABEL_SUPERVISORS):
                cur["supervisors"] = " ".join(cells[2:]).strip()
            elif is_label_cell(second, LABEL_DESCRIPTION):
                parts = [" ".join(cells[2:]).strip()] if any(cells[2:]) else []
                j = i + 1
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                        break
                    if looks_like_boundary(next_cells):
                        break
                    row_text = " ".join([c for c in next_cells if c])
                    if row_text:
                        parts.append(row_text)
                    j += 1
                cur["description"] = " ".join(parts).strip()
                i = j - 1

        i += 1

    # final append
    if cur["title"] or cur["primary_theme"] or cur["supervisors"] or cur["description"]:
        projects.append(cur)
    return projects

# --- parse single PDF ---
def parse_pdf(pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    all_projects: List[Dict[str, str]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                tables = page.extract_tables() or []
            except Exception:
                tables = []
            single = page.extract_table()
            if single and single not in tables:
                tables.append(single)
            for table in tables:
                rows = [[cell or "" for cell in row] for row in table]
                extracted = extract_projects_from_table(rows)
                if extracted:
                    all_projects.extend(extracted)

    for p in all_projects:
        for k, v in list(p.items()):
            p[k] = normalize(v)
    return all_projects

# --- process a single PDF and return list of projects (no csv write) ---
def projects_from_pdf(pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
    logger.info("Parsing PDF: %s", Path(pdf_path).resolve())
    return parse_pdf(pdf_path)

# --- process all PDFs into one CSV ---
def process_all_pdfs_to_one_csv(output_path: Optional[Union[str, Path]] = None) -> Path:
    if output_path is None:
        output_path = DEFAULT_COMBINED_CSV
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(RAW_PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDFs found in %s", RAW_PDF_DIR)
        pd.DataFrame(columns=["title", "primary_theme", "supervisors", "description"]).to_csv(output_path, index=False)
        logger.info("Wrote empty CSV headers to: %s", output_path.resolve())
        return output_path.resolve()

    all_projects: List[Dict[str, str]] = []
    for pdf in pdf_files:
        try:
            projs = projects_from_pdf(pdf)
            logger.info(" -> %d projects from %s", len(projs), pdf.name)
            all_projects.extend(projs)
        except Exception as e:
            logger.error("Failed to parse %s: %s", pdf.name, e)

    if all_projects:
        df = pd.DataFrame.from_records(all_projects)
    else:
        df = pd.DataFrame(columns=["title", "primary_theme", "supervisors", "description"])

    for col in ["title", "primary_theme", "supervisors", "description"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["title", "primary_theme", "supervisors", "description"]]
    df.to_csv(output_path, index=False)
    logger.info("Wrote %d rows to: %s", len(df), output_path.resolve())
    return output_path.resolve()

# --- process single PDF into CSV (existing behavior) ---
def process_pdf_to_csv(pdf_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
    pdf_path = Path(pdf_path)
    if pdf_path.parent == Path(".") or pdf_path.parent == Path(""):
        candidate = RAW_PDF_DIR / pdf_path.name
        if candidate.exists():
            pdf_path = candidate
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if output_path is None:
        output_path = CSV_OUTPUT_DIR / (pdf_path.stem + ".csv")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    projects = parse_pdf(pdf_path)

    if projects:
        df = pd.DataFrame.from_records(projects)
    else:
        df = pd.DataFrame(columns=["title", "primary_theme", "supervisors", "description"])

    for col in ["title", "primary_theme", "supervisors", "description"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["title", "primary_theme", "supervisors", "description"]]
    df.to_csv(output_path, index=False)
    logger.info("Wrote %d rows to: %s", len(df), output_path.resolve())
    return output_path.resolve()

# --- CLI ---
def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Extract projects from PDF(s) into CSV (pdfplumber).")
    parser.add_argument("pdf", nargs="?", default=None,
                        help="Optional PDF filename in data/raw_PDFs to process. If omitted, all PDFs in raw_PDFs/ are processed.")
    parser.add_argument("-o", "--output", help="explicit output CSV path (optional)", default=None)
    args = parser.parse_args()

    if args.pdf is None:
        out = process_all_pdfs_to_one_csv(args.output)
    else:
        out = process_pdf_to_csv(Path(args.pdf), args.output)
    logger.info("Done — CSV at: %s", out)

if __name__ == "__main__":
    _cli()