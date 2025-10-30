# DPhil Project Recommender Tool 
## The Team:
Thomas Shaw\
Oliver Staples\
Vaideha Sathe

## Problem Statement:
It is difficult to comprehensively search the large number of available rotation projects in the ILESLA Booklets. Broad sorting of projects into core themes limits search scope to narrower bands and restricts cross-theme project inspiration. This package aims to provide a text-to-text search tool to parse project booklets (in PDF format) and provide recommendations based on a user-created query string by developing a natural language-based search and recommendation system based on TF-IDF and embedding-based similarity scoring.

# Pipeline Units:
## PDF Loader
* Copies PDFs from a user-specified directory into the virtual environment.
* Parses project data from a PDF using `pdfplumber`.

## Preprocessor
* Tokenizes project descriptions from the dataframe and extracts POS tags using NLTK
* Lemmatizes tokens, removes stopwords and common words, and expands contractions.

## Recommender
* Takes three inputs: a long user query (>15 words), a file with tokenized descriptions, and the number of desired projects (N).
* Resolves filepath, vectorizes text with TF-IDF, and calculates cosine similarity between the query and project descriptions.
* Returns a DataFrame of the top N similar projects.

## CLI
* Provides a command-line interface (CLI) to run the full pipeline: Load PDFs → Process PDFs → Tokenize CSVs → Recommend projects.
* Allows flexible use from the project root with options for specific files, queries, and output locations.
mend() function.

## Installation Guide
# Create a virtual environment
# Install with Pip (recommended)
# Install from source

## Usage Guide
* Bring up the help menu with 
```
project-recommender -h
project-recommender -help
```
* Load PDFs by copying filepath of folder containing PDFs
```
project-recommender load your-path-goes-here
```
* Process PDFs
```
project-recommender process
```
* Tokenize descriptions
```
project-recommender tokenize
```
* Get recommendations
```
project-recommender recommend "your-prompt-goes-here"
```
