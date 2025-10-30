#!/usr/bin/env python3
"""
Lightweight CLI to run PDF -> CSV -> Tokenize -> Recommend pipeline.

Usage examples (from repo root):

# Process all PDFs in data/raw_PDFs and write combined CSV:
python -m project_recommender.cli process

# Process a specific PDF (filename looked for in data/raw_PDFs):
python -m project_recommender.cli process somefile.pdf -o data/project_CSVs/my_out.csv

# Tokenize an existing CSV (filename lives in data/project_CSVs/ or pass a path)
python -m project_recommender.cli tokenize projects_summary.csv

# Recommend (requires a tokenized CSV in data/tokenized_CSVs/ or pass path):
python -m project_recommender.cli recommend "I want epidemiology projects"

# Run full pipeline (process -> tokenize -> recommend)
python -m project_recommender.cli all --query "machine learning for biology"
"""
from __future__ import annotations

import argparse
import importlib
import logging
from pathlib import Path
import shutil
import contextlib

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


import importlib
import sys
from pathlib import Path

def _lazy_import_module(module_basename: str):
    """
    Import module as project_recommender.<module_basename>.
    If needed, add src/ to sys.path (calculated relative to this file).
    Raises ModuleNotFoundError with helpful diagnostics if import fails.
    """
    pkg_name = "project_recommender"
    full_name = f"{pkg_name}.{module_basename}"

    # 1) Try package import first (normal case)
    try:
        return importlib.import_module(full_name)
    except ModuleNotFoundError as e_pkg:
        # Continue to try to make it importable by adding src/
        pass

    # 2) Compute src directory (this file is at src/project_recommender/cli.py)
    here = Path(__file__).resolve()
    # here.parents[1] -> src (since here is src/project_recommender/cli.py)
    src_dir = here.parents[1]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # 3) Try again
    try:
        return importlib.import_module(full_name)
    except ModuleNotFoundError:
        # 4) Final helpful fallback: show diagnostics and raise a clear error
        msg = (
            f"Could not import {full_name!r}.\n"
            f"Checked package import and added src dir: {src_dir!s}\n"
            f"sys.path (first entries):\n  " + "\n  ".join(map(str, sys.path[:6])) + "\n\n"
            "Possible fixes:\n"
            "  - run this from the project root (the directory that contains 'src/')\n"
            "  - set PYTHONPATH=src when invoking python\n"
            "  - create src/project_recommender/__init__.py if missing\n"
            "  - install the package in editable mode: pip install -e .\n"
        )
        raise ModuleNotFoundError(msg)


@contextlib.contextmanager
def _push_cwd(p: Path):
    """Temporarily chdir to p (Path) and restore afterwards."""
    import os

    prev = Path.cwd()
    try:
        os.chdir(p)
        yield
    finally:
        os.chdir(prev)

def ensure_in_project_csvs(candidate: Path, pdf_loader):
    """
    Ensure `candidate` CSV is present in pdf_loader.CSV_OUTPUT_DIR.
    If candidate is already inside that dir, return it.
    If candidate is a path elsewhere, copy it into CSV_OUTPUT_DIR and return the target path.
    If candidate doesn't exist but is a plain filename, return CSV_OUTPUT_DIR / candidate (may not exist yet).
    """
    csv_dir = pdf_loader.CSV_OUTPUT_DIR
    csv_dir.mkdir(parents=True, exist_ok=True)

    candidate = Path(candidate)
    if candidate.exists():
        # if already in desired dir, return as-is
        try:
            if candidate.resolve().parent == csv_dir.resolve():
                return candidate
        except Exception:
            pass
        # copy into dir (overwrite if exists)
        target = csv_dir / candidate.name
        shutil.copy(candidate, target)
        logger.info("Copied %s -> %s", candidate, target)
        return target
    else:
        # not an existing path: treat as filename inside CSV_OUTPUT_DIR
        return csv_dir / candidate.name


def cmd_process(args: argparse.Namespace) -> Path:
    """
    Process PDFs into a single CSV (or single PDF -> CSV). Returns the produced CSV Path.
    """
    pdf_loader = _lazy_import_module("pdf_loader_plumber")
    if args.pdf is None:
        out = pdf_loader.process_all_pdfs_to_one_csv(args.output)
    else:
        out = pdf_loader.process_pdf_to_csv(Path(args.pdf), args.output)
    logger.info("CSV written: %s", out)
    return Path(out)


def cmd_tokenize(args: argparse.Namespace) -> Path:
    """
    Tokenize a CSV into data/tokenized_CSVs/.
    `args.csv` may be a filename (in data/project_CSVs/) or a path; we ensure the CSV is in project_CSVs.
    """
    pdf_loader = _lazy_import_module("pdf_loader_plumber")
    pre = _lazy_import_module("preprocessor")

    # ensure CSV lives in project_CSVs (preprocessor expects reading from data/project_CSVs/{filename})
    csv_candidate = Path(args.csv or "projects_summary.csv")
    csv_in_project_dir = ensure_in_project_csvs(csv_candidate, pdf_loader)

    # preprocessor.data_preprocessor expects a filename (reads from data/project_CSVs/{filename})
    # so call it from repo root to preserve relative paths
    repo_root = pdf_loader.REPO_ROOT
    with _push_cwd(repo_root):
        pre.data_preprocessor(csv_in_project_dir.name)

    tokenized_dir = repo_root / "data" / "tokenized_CSVs"
    tokenized_path = tokenized_dir / csv_in_project_dir.name
    logger.info("Tokenized CSV: %s", tokenized_path)
    return tokenized_path.resolve()


def cmd_recommend(args: argparse.Namespace) -> str:
    """
    Recommend using a tokenized CSV. If tokenized_csv not provided, default to
    data/tokenized_CSVs/projects_summary.csv inside the repo root.
    """
    pdf_loader = _lazy_import_module("pdf_loader_plumber")
    rec = _lazy_import_module("recommender")

    if args.tokenized_csv:
        token_csv = Path(args.tokenized_csv)
        if not token_csv.exists():
            # maybe it's in the repo tokenized dir
            token_csv = pdf_loader.REPO_ROOT / "data" / "tokenized_CSVs" / f"tokenized_{token_csv.name}"
    else:
        token_csv = pdf_loader.REPO_ROOT / "data" / "tokenized_CSVs" / "tokenized_projects_summary.csv"

    if not token_csv.exists():
        logger.error("Tokenized CSV not found: %s", token_csv)
        raise FileNotFoundError(token_csv)

    # Ensure amount is present and is an int
    amount = int(getattr(args, "amount", 10) or 10)
    logger.info("Running recommendation: query=%r, tokenized_csv=%s, amount=%d",
                args.query, token_csv, amount)

    result = rec.recommend(args.query, str(token_csv), amount_wanted=amount)
    # print for CLI use
    print(result)
    return result



def cmd_all(args: argparse.Namespace) -> Path:
    """
    Run full pipeline: process -> tokenize -> (optional recommend).
    Returns tokenized CSV path (or raises).
    """
    # 1) process
    out_csv = cmd_process(argparse.Namespace(pdf=args.pdf, output=args.output))

    # 2) tokenize (pass filename)
    tokenized_path = cmd_tokenize(argparse.Namespace(csv=Path(out_csv).name))

    # 3) optional recommend
    if getattr(args, "query", None):
        # forward amount from top-level args to the recommend call
        cmd_recommend(argparse.Namespace(
            query=args.query,
            tokenized_csv=str(tokenized_path),
            amount=getattr(args, "amount", 10)
        ))

    else:
        logger.info("Pipeline finished. Tokenized CSV at: %s", tokenized_path)

    return Path(tokenized_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-recommender", description="PDF -> CSV -> Tokenize -> Recommend CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("process", help="Process PDF(s) into CSV(s)")
    p.add_argument("pdf", nargs="?", default=None, help="Optional PDF filename in data/raw_PDFs to process. If omitted, all PDFs are processed.")
    p.add_argument("-o", "--output", help="Explicit output CSV path (optional)", default=None)
    p.set_defaults(func=cmd_process)

    t = sub.add_parser("tokenize", help="Tokenize a project CSV into data/tokenized_CSVs")
    t.add_argument("csv", nargs="?", default="projects_summary.csv", help="CSV filename or path in data/project_CSVs to tokenize (default projects_summary.csv)")
    t.set_defaults(func=cmd_tokenize)

    r = sub.add_parser("recommend", help="Get a project recommendation from a tokenized CSV")
    r.add_argument("query", help="User query string")
    r.add_argument("--tokenized-csv", dest="tokenized_csv", help="Path to tokenized CSV (optional)", default=None)
    r.add_argument("--amount", "-n", dest="amount", type=int, default=10,
                help="Number of recommendations to return (default: 10)")
    r.set_defaults(func=cmd_recommend)


    a = sub.add_parser("all", help="Run full pipeline: process -> tokenize -> (recommend)")
    a.add_argument("pdf", nargs="?", default=None, help="Optional PDF filename to process (default: all PDFs)")
    a.add_argument("-o", "--output", help="Explicit CSV output path for processing step (optional)", default=None)
    a.add_argument("--query", help="Optional user query to run recommender at the end", default=None)
    a.add_argument("--amount", "-n", dest="amount", type=int, default=10,
                help="Number of recommendations to return when running with --query (default: 10)")
    a.set_defaults(func=cmd_all)


    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as e:
        logger.error("Error: %s", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
