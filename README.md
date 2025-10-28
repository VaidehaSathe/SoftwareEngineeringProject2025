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
Given a PDF file containing projects, outputs a csv file with columns ["title:","supervisors":,"description"]\
Extraction logic with pdfplumber.

## Preprocessor
Takes the project description strings from the dataframe and tokenizes them using the NLTK Word Tokenizer.\
Extracts POS tags for the tokens.\
Removes inflectional endings of the tokens using the NLTK lemmatizer.\
Removes common words (including articles and english stopwords).\
Replaces any contractions with their original words.

## Recommender

## CLI
