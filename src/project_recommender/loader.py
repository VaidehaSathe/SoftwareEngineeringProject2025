# Date 29/10/2025
# DESCRIPTION: This module contains a function called move_pdf, which takes as an input
# the filepath of the directory that you want to move PDFs from, then copies said PDFs
# into a different directory, called data
#
# As an output, it returns the name of the directory that they were copied into (data),
# a list of the PDFs that were copied, and the number of files that were copied.

from pathlib import Path
import shutil

def move_pdf(filepath):
    """ Input the filepath that you want to move the PDF files from
    This function will move them to data/raw_PDFs. """

    #Resolve the filepath
    filepath_resolved = Path(filepath).resolve()

    #Find the PDFs
    pdfs = [file for file in filepath_resolved.rglob("*.pdf") if file.is_file()]
    if pdfs == []:
        return("There are no PDFs in this filepath")

    #Find the directory that is two directories 'up'
    two_up = filepath_resolved.resolve().parents[2]

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