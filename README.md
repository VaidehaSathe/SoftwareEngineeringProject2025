# DPhil Project Recommender Tool 
## The Team
Thomas Shaw\
Oliver Staples\
Vaideha Sathe

## What does this do?
`project-recommender` is a python package that finds ILESLA projects most suited for you. Simply save the project booklets from the canvas website, run this package along with a description of what you want to explore, and let clever natural language processing do its thing. 

This is suitable for those who want to...
* explore potential projects in simple human language
* get recommdations across ALL themes
* find matches to your interests that you may have missed

## Problem Statement
It is difficult to comprehensively search the large number of available rotation projects in the ILESLA Booklets. Broad sorting of projects into core themes limits search scope to narrower bands and restricts cross-theme project inspiration. This package aims to provide a text-to-text search tool to parse project booklets (in PDF format) and provide recommendations based on a user-created query string by developing a natural language-based search and recommendation system based on TF-IDF and embedding-based similarity scoring.

## Installation Guide
Follow these steps exactly for the program to work.
### Create a virtual environment
```
# Create a virtual environment called venv
python3 -m venv venv 

# On Windows
venv\Scripts\Activate.ps1

# On macOS and Linux
source venv/bin/activate
```

### Install with Pip (recommended)
```
pip install -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  project-recommender==0.0.1
```
### Install from source (for advanced users)#
* Clone the repository 
```
# Clone over https
git clone https://github.com/VaidehaSathe/SoftwareEngineeringProject2025.git

# Alternatively, clone over SSH
git@github.com:VaidehaSathe/SoftwareEngineeringProject2025.git
```
* Build the package  
```
# Needs to be in source folder
python -m pip install --upgrade build
python -m build
```
This creates files in the dist/ folder, like
```
dist/project_recommender-0.0.1-py3-none-any.whl
dist/project_recommender-0.0.1.tar.gz
```
* Build from wheel
```
python -m pip install dist/project_recommender-0.0.1-py3-none-any.whl
```

## Simple Usage Guide
* As a prerequisite, download all project booklets from the Canvas page and place them in a folder. 

* Bring up the help menu with 
```
project-recommender -h
project-recommender -help
```
* Load PDFs by copying filepath of folder containing PDFs (get the filepath to your folder by right click → copy as path)
```
project-recommender load (absolute)path/to/your/pdf/folder
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
Words or phrases in your input prompt that are similar to those in project descriptions return a 'mini-score'. The final similarity score provided with each recommended project is the sum of all of these mini-scores, so is a measure of how many small 'matches' there.

Note that if you put in another prompt and it recommends projects with higher similarity scores than with your previous prompt, it is not necessarily an indicator of a 'better match' - you might have just put more words into the input. On average, the more words you put in, the higher the score.

The input prompt also has to be longer than 15 words, in order to give more meaningful responses.


## Advanced Usage Guide
In general, each command takes the form `project-recommender <command> [options]`. Each command `load` `process` `tokenize` `all` has several options.

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

# Change number of results to 5
project-recommender recommend "your-prompt-goes-here" -n 5

# Specify particular tokenized CSV
project-recommender recommend "your-prompt-goes-here" --tokenized-csv data/tokenized_CSVs/tokenized_my_booklet.csv
```

## Modules
### PDF Loader
* Copies PDFs from a user-specified directory into the virtual environment.
* Parses project data from tabularized PDF using `pdfplumber`.

### Preprocessor
* Tokenizes project descriptions from the dataframe and extracts POS (Part-of-Speech) tags using NLTK.
* Lemmatizes tokens, removes stopwords and common words, and expands contractions.

### Recommender
* Takes three inputs: a user query of at least 15 words, a file with tokenized descriptions, and the number of desired projects.
* Resolves filepath, vectorizes text with TF-IDF (Term Frequency-Inverse Document Frequency), and calculates cosine similarity between the query and project descriptions.
* Returns N projects (by default, 10) based on a similarity score.

### CLI
* Provides a command-line interface (CLI) to run the full pipeline: Load PDFs → Process PDFs → Tokenize CSVs → Recommend projects.
* Allows flexible use from the project root with options for specific files, queries, and output locations.
