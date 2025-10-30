# DPhil Project Recommender Tool 
## The Team:
Thomas Shaw\
Oliver Staples\
Vaideha Sathe

## Problem Statement:
It is difficult to comprehensively search the large number of available rotation projects in the ILESLA Booklets. Broad sorting of projects into core themes limits search scope to narrower bands and restricts cross-theme project inspiration. This package aims to provide a text-to-text search tool to parse project booklets (in PDF format) and provide recommendations based on a user-created query string by developing a natural language-based search and recommendation system based on TF-IDF and embedding-based similarity scoring.

## Modules:
### PDF Loader
* Copies PDFs from a user-specified directory into the virtual environment.
* Parses project data from a PDF using `pdfplumber`.

### Preprocessor
* Tokenizes project descriptions from the dataframe and extracts POS tags using NLTK
* Lemmatizes tokens, removes stopwords and common words, and expands contractions.

### Recommender
* Takes three inputs: a long user query (>15 words), a file with tokenized descriptions, and the number of desired projects (N).
* Resolves filepath, vectorizes text with TF-IDF, and calculates cosine similarity between the query and project descriptions.
* Returns N projects based on a similarity score.

### CLI
* Provides a command-line interface (CLI) to run the full pipeline: Load PDFs → Process PDFs → Tokenize CSVs → Recommend projects.
* Allows flexible use from the project root with options for specific files, queries, and output locations.
mend() function.

## Installation Guide
### Create a virtual environment
### Install with Pip (recommended)
### Install from source

## Simple Usage Guide
* Bring up the help menu with 
```
project-recommender -h
project-recommender -help
```
* Load PDFs by copying filepath of folder containing PDFs
```
project-recommender load your-path-goes-here
```
* Generate recommendations based on your query
```
project-recommender all "Your query goes here"
```

## Example Usage
```
project-recommender load /home/project-folder/
project-recommender all "I want to learn about machine learning methods for collective cell movement. I would like to work with industry, and I want to use mathematical modelling in my research."

# output
project-title supervisors department  score
title1        supervisor1 department1 0.98
title2        supervisor2 department2 0.44
title3        supervisor3 department3 0.12
...
```

## Advanced Usage Guide
In general, each command takes the form `project-recommender <command> [options]`. Each command `load` `process` `tokenize` `all` has several manual options.

* **load**: copies PDFs from system's working directory (/path/to/project_pdfs) to inside your venv.
```
project-recommender load /path/to/project_pdfs
```

* **process**: extracts project data from one or more PDFs
```
# default (process all PDFs at once)
project-recommender process

# Process a specific PDF
project-recommender process "Sample Project Booklet.pdf"

# Specify explicit CSV output path
project-recommender process -o data/project_CSVs/my_booklet.csv
```

* **tokenize**: tokenizes the description text in a CSV file
```
# default (proceses project_summary.csv)
project-recommender tokenize

# Specify particular text CSV
project-recommender tokenize data/project_CSVs/my_booklet.csv
```

* **recommend**: give top-N recommendations for a given text query
```
# default (N=10 recommendations)
project-recommender recommend "your-prompt-goes-here"

# Change number of results
project-recommender recommend "your-prompt-goes-here" -n 5

# Specify particular tokenized CSV
project-recommender recommend "your-prompt-goes-here" --tokenized-csv data/tokenized_CSVs/tokenized_my_booklet.csv

```
```
