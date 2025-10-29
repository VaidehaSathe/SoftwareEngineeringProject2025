Project Repository for the ILESLA DTP 2025 Software Engineering course.

# DPhil Project Recommender Tool 
## The Team:
Thomas Shaw\
Oliver Staples\
Vaideha Sathe

## Problem Statement:
It is difficult to comprehensively search the large number of available rotation projects in the ILESLA Booklets. Broad sorting of projects into core themes limits search scope to narrower bands and restricts cross-theme project inspiration. This package aims to provide a text-to-text search tool to parse project booklets (in PDF format) and provide recommendations based on a user-created query string by developing a natural language-based search and recommendation system based on TF-IDF and embedding-based similarity scoring.

# Pipeline Units:
## PDF Loader
* Given a PDF file containing projects, outputs a csv file with columns ["title:","supervisors":,"description"]
* Extraction logic with `pdfplumber`.

## Preprocessor
* Takes the project description strings from the dataframe and tokenizes them using the NLTK Word Tokenizer.
* Extracts POS tags for the tokens.
* Removes inflectional endings of the tokens using the NLTK lemmatizer.
* Removes common words (including articles and english stopwords).
* Replaces any contractions with their original words.

## Recommender
* Takes three inputs: a long user query (>15 words), a tokenized CSV filename, and the number of desired projects (N).
* Resolves the CSV path, vectorizes text with TF-IDF, and calculates cosine similarity between the query and project descriptions.
* Returns a DataFrame of the top N projects with columns: title, primary_theme, supervisors, and score.

## CLI


For these to work, you need to be in the root folder. That is, in /SoftwareEngineeringProject2025. Not in /src/, not in /project_recommender/. The general command line structure is `python -m project_recommender.cli <command> <query>`. There are four commands: ```-process, -tokenize, recommend, -all```

**-process**

This takes PDFs in data/raw_PDFs/ and write CSV(s) into data/project_CSVs

```
process -o [pdf] 
```

-o is an optional field. It outputs the CSV location.
[pdf] is an optional field, it takes the name of the PDF file. Left empty, it will read all PDFs in raw_PDFs.

**-tokenize**

This takes a CSV file in data/project_CSVs and tokenizes the description, writing another file in data/tonkeized_CSVs

`tokenize [csv]`

[csv] is an optional field. It takes the name of the csv, left empty will read /projects_summary.csv

**-recommend**

Calls the recommend() function.

```recommend "query text here" --tokenized-csv --amount```

--tokenized-csv is an optional field. It takes the filepath of the tokenized-csv.
--amount is a necessary field. It is the nunmber of projects you want to select.

**-all**

Does all of above.

## Developer Usage

```
# General CLI command structure

PYTHONPATH=src python -m project_recommender.cli <subcommand> [options]
```

```
# Process all PDFs
PYTHONPATH=src python -m project_recommender.cli process

# Process single PDF and write to custom CSV
PYTHONPATH=src python -m project_recommender.cli process somefile.pdf -o data/project_CSVs/my_out.csv
```

```
# Tokenize default projects_summary.csv
PYTHONPATH=src python -m project_recommender.cli tokenize

# Tokenize a specific CSV path
PYTHONPATH=src python -m project_recommender.cli tokenize path/to/my.csv
```

```
# Default 10 results (tokenized CSV in repo)
PYTHONPATH=src python -m project_recommender.cli recommend "I want biology projects"

# Specify tokenized CSV and 5 results
PYTHONPATH=src python -m project_recommender.cli recommend "I want biology projects" --tokenized-csv tokenized_projects_summary.csv --amount 5
```

```
# Full pipeline for all PDFs, no recommend
PYTHONPATH=src python -m project_recommender.cli all

# Full pipeline for a specific PDF and then recommend 7 results
PYTHONPATH=src python -m project_recommender.cli all mydoc.pdf -o data/project_CSVs/out.csv --query "epidemiology machine learning" --amount 7
```
## User commands
Strictly speaking, these commands should be invoked with 

```
python -m project_recommender.cli <subcommand> [options]
```

This should be possible later.
To run this command instead, go to the root and do `pip install -e .`
