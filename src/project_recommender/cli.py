# cli.py
import argparse
from pathlib import Path
import sys


"""
To write out a .csv python cli.py ../../data/fake-project-list.pdf --write-txt -o parsed.csv
To read a .txt file python cli.py ../../data/fake-project-list.txt
To read a PDF  python cli.py ../../data/fake-project-list.txt
"""

from pdf_loader import pdf_load
from extractor import text_to_projects_df_from_string

def resolve_path_maybe_repo_root(p: Path) -> Path:
    """If path exists return it; else try repo root (two levels up) + p."""
    if p.exists():
        return p
    repo_root = Path(__file__).resolve().parents[2]  # adjust for src/project_recommender layout
    alt = (repo_root / p).resolve()
    return alt if alt.exists() else p

def main():
    p = argparse.ArgumentParser(description="Minimal CLI: PDF -> extractor -> DataFrame")
    p.add_argument("input", help="Path to .pdf or .txt file")
    p.add_argument("-o", "--output", help="Optional output file (.csv or .json). If omitted prints DataFrame.")
    p.add_argument("--write-txt", action="store_true",
                   help="If input is PDF, also write a sidecar .txt file using pdf_loader (default: no)")
    args = p.parse_args()

    input_path = Path(args.input)
    input_path = resolve_path_maybe_repo_root(input_path)

    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    # 1) obtain text (PDF -> pdf_loader, TXT -> read directly)
    if input_path.suffix.lower() == ".pdf":
        # pdf_load returns (text, output_txt_path)
        text, txt_path = pdf_load(str(input_path), write_txt=args.write_txt)
        print(f"[cli] pdf_loader returned {len(text)} characters (sidecar: {txt_path or 'not written'})")
    else:
        text = input_path.read_text(encoding="utf-8")
        print(f"[cli] read text file {input_path} ({len(text)} characters)")

    # 2) pass text string into extractor to get DataFrame
    try:
        df = text_to_projects_df_from_string(text)
    except Exception as e:
        print(f"[cli] extractor failed: {e}", file=sys.stderr)
        sys.exit(3)

    # 3) output: print or save based on args
    if args.output:
        out = Path(args.output)
        suf = out.suffix.lower()
        if suf == ".csv":
            df.to_csv(out, index=False)
            print(f"[cli] wrote CSV to {out}")
        elif suf == ".json":
            df.to_json(out, orient="records", indent=2)
            print(f"[cli] wrote JSON to {out}")
        else:
            # default to CSV if unknown extension
            df.to_csv(out.with_suffix(".csv"), index=False)
            print(f"[cli] unknown extension; wrote CSV to {out.with_suffix('.csv')}")
    else:
        # compact print
        # make wide enough for long descriptions; adjust or remove if you prefer default pandas display
        import pandas as _pd
        _pd.set_option("display.max_colwidth", 300)
        print(df.to_string(index=False))

if __name__ == "__main__":
    main()
