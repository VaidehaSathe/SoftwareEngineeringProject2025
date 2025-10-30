# loader.py
# Date 29/10/2025

"""
Description: Moves PDF files from a specified directory to a local folder called data/raw_PDFs.
Input: Filepath of a folder containing any PDFs the user wants read
Output: 
- The folders /data/raw_PDFs, data/project_CSVs, and data/tokenized_CSVs in the repo root (where the script runs from)
- Moves the PDFs from the local folder to /data/raw_PDFs

I used os.path.abspath and os.path.dirname instead of explicitly calling '..' so it should be compatable with different OSes.
"""

from pathlib import Path
import shutil
import os

def repo_root_guess() -> Path:
    try:
        return Path(__file__).resolve().parents[2]
    except Exception:
        return Path.cwd()

REPO_ROOT = repo_root_guess()

# primary data dirs used by the pipeline
RAW_PDF_DIR = (REPO_ROOT / "data" / "raw_PDFs").resolve()
CSV_OUTPUT_DIR = (REPO_ROOT / "data" / "project_CSVs").resolve()
CSV_TOK_OUTPUT_DIR = (REPO_ROOT / "data" / "tokenized_CSVs").resolve()

# ensure directories exist (idempotent)
RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CSV_TOK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def move_pdf(filepath):
    """ Input the filepath that you want to move the PDF files from
    This function will move them to data/raw_PDFs. """
    
    filepath_resolved_folder = os.path.abspath(os.path.dirname(__file__))
    # home/teaching/SoftwareEngineeringProject2025/src/project_recommender/loader.py

    # resolve the filepath of the folder containing PDFs
    filepath_resolved = Path(filepath).resolve()
    # print(filepath, filepath_resolved)

    #Find the PDFs
    pdfs = [file for file in filepath_resolved.rglob("*.pdf") if file.is_file()]
    if pdfs == []:
        return("There are no PDFs in this filepath")
    # else: print("PDF found at:",filepath)

    # Find the directory that is two directories 'up'. os.path.dirname finds the directory directly above its argument.
    # Path() converts the string to a path.
    # two_up = filepath_resolved_folder.resolve().parents[2]
    two_up = Path(os.path.dirname(os.path.dirname(filepath_resolved_folder)))

    # print(two_up)

    #Find the directory called 'data'
    data_directory = None
    raw_PDFs_directory = None
    for directory in two_up.iterdir():
        if directory.is_dir() and directory.name.lower() == "data":
            data_directory = directory
            break
    if data_directory == None:
        return("There is no data directory, or it could not be found")

    #Find the directory called 'raw_PDFs'
    for directory in data_directory.iterdir():
        if directory.is_dir() and directory.name == "raw_PDFs":
            raw_PDFs_directory = directory
    if raw_PDFs_directory == None:
        return("There is no raw_PDFs directory, or it could not be found")

    #Copies the PDFs into the data directory and counts them
    copied=[]
    for pdf in pdfs:
        destination = raw_PDFs_directory / pdf.name
        shutil.copy2(pdf,destination)
        copied.append(destination)
    
    return {"Copied into": raw_PDFs_directory, "Copied files": copied, "Number of files copied": len(copied)}

# Test
# move_pdf("zzz") 