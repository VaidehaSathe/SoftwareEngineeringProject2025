""" 
recommender.py
Date 28/10/2025
--------------------------------------------------------#
DESCRIPTION: This function takes three inputs:
1. a user query, which is a string > 15 words
2. the name of a tokenized .csv file in the tokenized_CSVs folder
3. the number of projects that the user wants, an integer: N

It resolves the filepath of the csv file with pathlib.
It vectorizes with TF-IDF and finds cosine similarity between 
query and tokenized project descriptions.
It takes the top N projects by similarity, and creates a new dataframe object.
This has the keys (['title', 'primary_theme', 'supervisors', 'score']
It returns this new dataframe object.

DO NOT RUN THIS FILE DIRECTLY. If you do, remove the dot from from .preprocessor
When running this file, go to /SoftwareEngineeringProject2025, then
PYTHONPATH=src python -m project_recommender.cli recommend "I want biology projects"
--tokenized-csv tokenized_projects_summary.csv

Alternatively, do
# from project root (/SoftwareEngineeringProject2025)
pip install -e .
python -m project_recommender.cli recommend "I want biology projects"
Test code at bottom.
--------------------------------------------------------#
"""
from pathlib import Path

import pandas as pd
# import nltk
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessor import query_preprocessor

tfidfvec = TfidfVectorizer()

def recommend(user_input,tokenized_data_csv,amount_wanted):
    """
    Takes a user statement and .csv file, and returns the
    project title which matches closest to the user statement

    Args: User statement (e.g. 'I am James, I'm interested in the studying the pandemic)
    and .csv file containing tokenized data (processed versions of the project descriptions)

    Returns: The project title which is 'closest' to the user statement
    """

    # Check that the user input is greater than 15 words

    if len(user_input.split())<=15:
        return "Your statement is too short!"
    # read the .csv file
    tokenized_data = pd.read_csv(tokenized_data_csv)

    # process the user statement
    user_tokens = query_preprocessor(user_input)

    # vectorize project descriptions
    tfidf_data = tfidfvec.fit_transform(tokenized_data['tokenized_description'])

    # transform user input
    user_tokens_list = user_tokens.split(" ")
    tfidf_user = tfidfvec.transform(user_tokens_list)

    # compute cosine similarity
    cos_sim = cosine_similarity(tfidf_user, tfidf_data)

    # sum similarity scores per project
    project_scores = np.sum(cos_sim, axis=0)

    # sort by highest score
    indices_sorted = np.argsort(project_scores)[::-1]
    no_zeros = indices_sorted[project_scores[indices_sorted] > 0]

    # limit to requested amount
    no_zeros_correct_amount = no_zeros[:amount_wanted]

    # collect matching projects with all key info
    projects = []
    for i in no_zeros_correct_amount:
        projects.append([
            tokenized_data.loc[i, 'title'],
            tokenized_data.loc[i, 'primary_theme'],
            tokenized_data.loc[i, 'supervisors'],
            project_scores[i]
        ])

    # warn if fewer than requested
    if len(projects) < amount_wanted:
        print(f"There are only {len(projects)} recommendations available.")

    # return nicely formatted DataFrame
    final_projects = pd.DataFrame(
        projects,
        columns=['title', 'primary_theme', 'supervisors', 'score']
    )

    return final_projects

# Clever pathhandling magic

# If this file is located at src/projects_recommend/..., then:
HERE = Path(__file__).resolve().parent           # src/projects_recommend
PROJECT_ROOT = HERE.parent.parent                 # project_root

def resolve_data_path(path_like: str) -> Path:
    """
    Takes string of pdf to get path
    """

    p = Path(path_like)
    # 1) Absolute path given
    if p.is_absolute():
        return p
    # 2) If it already exists relative to current working dir, use it
    if (Path.cwd() / p).exists():
        return (Path.cwd() / p).resolve()
    # 3) Try relative to the project root (project_root/data/...)
    candidate = PROJECT_ROOT / p
    if candidate.exists():
        return candidate.resolve()
    # 4) If the user passed only a filename, try project_root/data/tokenized_CSVs/<name>
    candidate2 = PROJECT_ROOT / "data" / "tokenized_CSVs" / p.name
    if candidate2.exists():
        return candidate2.resolve()
    # nothing found — raise helpful error
    raise FileNotFoundError(
        f"Could not find file {path_like!r}. Tried:\n"
        f"  - {Path.cwd() / p}\n"
        f"  - {candidate}\n"
        f"  - {candidate2}\n"
        f"Adjust the path or pass an absolute path."
    )

# A quick test to check that this is in fact working.
# Uncomment the next code blocks, and then run this file (top right arrow)
# The output should be like:

#                                                title  ...     score
# 0  A53 Uncovering novel microglial biology throug...  ...  0.541533
# 1  A5 Developing viral dynamics models for optimi...  ...  0.486942
# 2  A60 Dynamic adaptation of plasma cell differen...  ...  0.348137
# 3  A35 Decoding the Human Gut Immune Landscape Th...  ...  0.345850
# 4  A48 Structural mechanisms of T cell receptor r...  ...  0.342880
# 5  A4 Investigating the impact of microbiome vari...  ...  0.307147
# 6  A22 Which cytoskeletal proteins organise the m...  ...  0.303176
# 7  A17 Molecular mechanisms underlying viral evol...  ...  0.291739
# 8  A46 Extracellular Sphingolipids as Drivers and...  ...  0.286518
# 9  A57 Using super-resolution microscopy to under...  ...  0.271357

# projs = recommend(
#     "I want to know about biology cell movement and use
#           machine learning with python for mathematical modelling",
#     tokenized_data_csv=resolve_data_path("tokenized_projects_summary.csv"),
#     amount_wanted=10)

# # Prints the whole dataframe object (10 rows x N cols (user specified))
# print(projs)

# # Checks that the column titles are correct
# Should return:
# (Index(['title', 'primary_theme', 'supervisors', 'score'], dtype='object'))

# print(projs.keys())
