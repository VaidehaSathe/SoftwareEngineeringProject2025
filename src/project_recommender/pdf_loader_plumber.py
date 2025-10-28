# pdf_loader_plumber.py

# Date: 28/10/2025 
#--------------------------------------------------------#
# Description: This is a updated PDF -> raw text script that uses pdfplumber
# Functionality: PDF (filepath) --> csv file with columns [title, supervisors, project description]
# 
# To run, cd into project_recommender, and then do: python pdf_loader_plumber.py [filepath]
# It will output project_summary.csv under the data folder next to src. 
#
# HOW TO
# python pdf_loader_plumber.py somefile.pdf
#
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
STOP_DESCRIPTION_LABELS = {"reasonable expected outcome", "reasonab"}

# --- repo / data dirs ---
def repo_root_guess() -> Path:
    """Lightweight repo root guess: two levels up from this file if that exists, else cwd."""
    try:
        return Path(__file__).resolve().parents[2]
    except Exception:
        return Path.cwd()

REPO_ROOT = repo_root_guess()
RAW_PDF_DIR = (REPO_ROOT / "data" / "raw_PDFs").resolve()
CSV_OUTPUT_DIR = (REPO_ROOT / "data" / "project_CSVs").resolve()

RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logger.debug("REPO_ROOT: %s", REPO_ROOT)
logger.debug("RAW_PDF_DIR: %s", RAW_PDF_DIR)
logger.debug("CSV_OUTPUT_DIR: %s", CSV_OUTPUT_DIR)

# --- small helpers ---
def normalize(s: Optional[str]) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()

def is_label_cell(text: Optional[str], target: str) -> bool:
    if not text:
        return False
    return target in normalize(text).lower()

# --- core extraction (kept simple & robust) ---
def extract_projects_from_table(table_rows: List[List[Optional[str]]]) -> List[Dict[str, str]]:
    projects: List[Dict[str, str]] = []
    cur = {"title": "", "supervisors": "", "description": ""}
    i = 0
    while i < len(table_rows):
        cells = [normalize(c) for c in table_rows[i]]
        first_non_empty_idx = next((j for j, c in enumerate(cells) if c), None)
        first_cell = cells[first_non_empty_idx] if first_non_empty_idx is not None else ""

        if is_label_cell(first_cell, LABEL_TITLE):
            # push previous if any
            if cur["title"] or cur["supervisors"] or cur["description"]:
                projects.append(cur)
                cur = {"title": "", "supervisors": "", "description": ""}

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
                    if any(is_label_cell(c, LABEL_SUPERVISORS) or is_label_cell(c, LABEL_DESCRIPTION) for c in next_cells if c):
                        break
                    parts.extend([c for c in next_cells if c])
                    j += 1
                cur["title"] = " ".join(parts).strip()

        elif is_label_cell(first_cell, LABEL_SUPERVISORS):
            rest = " ".join(cells[first_non_empty_idx + 1 :]).strip()
            if rest:
                cur["supervisors"] = rest
            else:
                j = i + 1
                parts = []
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(is_label_cell(c, LABEL_DESCRIPTION) or is_label_cell(c, LABEL_TITLE) for c in next_cells if c):
                        break
                    parts.extend([c for c in next_cells if c])
                    j += 1
                cur["supervisors"] = " ".join(parts).strip()

        elif is_label_cell(first_cell, LABEL_DESCRIPTION):
            # gather description lines until a stop label
            parts = []
            rest = " ".join(cells[first_non_empty_idx + 1 :]).strip()
            if rest:
                parts.append(rest)
            j = i + 1
            while j < len(table_rows):
                next_cells = [normalize(x) for x in table_rows[j]]
                if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                    break
                row_text = " ".join([c for c in next_cells if c]).strip()
                if row_text:
                    parts.append(row_text)
                j += 1
            cur["description"] = " ".join(parts).strip()
            i = j - 1  # skip ahead to last read row

        else:
            # fallback: check second column for label (some styles)
            second = cells[1] if len(cells) > 1 else ""
            if is_label_cell(second, LABEL_TITLE):
                cur["title"] = " ".join(cells[2:]).strip()
            elif is_label_cell(second, LABEL_SUPERVISORS):
                cur["supervisors"] = " ".join(cells[2:]).strip()
            elif is_label_cell(second, LABEL_DESCRIPTION):
                parts = [" ".join(cells[2:]).strip()] if any(cells[2:]) else []
                j = i + 1
                while j < len(table_rows):
                    next_cells = [normalize(x) for x in table_rows[j]]
                    if any(any(is_label_cell(c, stop) for stop in STOP_DESCRIPTION_LABELS) for c in next_cells if c):
                        break
                    row_text = " ".join([c for c in next_cells if c])
                    if row_text:
                        parts.append(row_text)
                    j += 1
                cur["description"] = " ".join(parts).strip()
                i = j - 1

        i += 1

    # final append
    if cur["title"] or cur["supervisors"] or cur["description"]:
        projects.append(cur)
    return projects

# --- parse PDF file ---
def parse_pdf(pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    all_projects: List[Dict[str, str]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # prefer extract_tables if available, but fallback to extract_table
            try:
                tables = page.extract_tables() or []
            except Exception:
                tables = []
            single = page.extract_table()
            if single and single not in tables:
                tables.append(single)
            for table in tables:
                # normalize None -> ""
                rows = [[cell or "" for cell in row] for row in table]
                extracted = extract_projects_from_table(rows)
                if extracted:
                    all_projects.extend(extracted)

    # normalize whitespace for each field
    for p in all_projects:
        for k, v in list(p.items()):
            p[k] = normalize(v)
    return all_projects

# --- process + write CSV (works reliably) ---
def process_pdf_to_csv(pdf_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
    pdf_path = Path(pdf_path)
    # If user passed only a filename (no directory), prefer RAW_PDF_DIR
    if not pdf_path.parent or pdf_path.parent == Path("." ):
        candidate = RAW_PDF_DIR / pdf_path.name
        if candidate.exists():
            pdf_path = candidate
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # default output file: data/project_CSVs/<pdf_stem>.csv
    if output_path is None:
        output_path = CSV_OUTPUT_DIR / (pdf_path.stem + ".csv")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Parsing PDF: %s", pdf_path.resolve())
    projects = parse_pdf(pdf_path)

    # build DataFrame robustly
    if projects:
        df = pd.DataFrame.from_records(projects)
    else:
        # ensure headers even with no projects
        df = pd.DataFrame(columns=["title", "supervisors", "description"])

    # ensure consistent column order
    for col in ["title", "supervisors", "description"]:
        if col not in df.columns:
            df[col] = ""
    df = df[["title", "supervisors", "description"]]

    # final: write CSV (force flush by not using any temp ambiguity)
    df.to_csv(output_path, index=False)
    logger.info("Wrote %d rows to: %s", len(df), output_path.resolve())
    return output_path.resolve()

# --- CLI entrypoint ---
def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Extract projects from a PDF into CSV (pdfplumber).")
    parser.add_argument("pdf", help="PDF filename (if only filename given, looked for in data/raw_PDFs/)")
    parser.add_argument("-o", "--output", help="explicit output CSV path (optional)", default=None)
    args = parser.parse_args()

    # resolve input param: either explicit path or filename inside RAW_PDF_DIR
    pdf_param = Path(args.pdf)
    if args.output:
        out = process_pdf_to_csv(pdf_param, args.output)
    else:
        out = process_pdf_to_csv(pdf_param)
    logger.info("Done — CSV at: %s", out)

if __name__ == "__main__":
    _cli()
