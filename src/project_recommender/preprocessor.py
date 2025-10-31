"""
preprocessor.py
Date: 27/10/2025

Description: This module contains functions to preprocess text data to feed into the recommender module.
- data_preprocessor: Tokenizes all description elements from Extracted Data CSV
- query_preprocessor: Tokenizes input text string for recommender

Inputs: Origanal Text

Outputs: Tokenized Text
"""

import pandas as pd
import nltk

nltk_resources=['punkt', 'averaged_perceptron_tagger', 'wordnet', 'stopwords']

def add_nltk_resources():
    """
    Checks if the above nltk resources are available
    If they aren't, download them
    """
    missing = []
    for resource in nltk_resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            missing.append(resource)
    if missing:
        for resource in missing:
            nltk.download(resource,quiet=True)

add_nltk_resources()

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
lemmatizer = WordNetLemmatizer()

stop_words = set(stopwords.words('english'))

verb_codes = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}

def preprocess_text(text):
    """
    Preprocesses the input text by tokenizing, removing stop words, and lemmatizing verbs.
    
    Args:
        text (str): The input text string to preprocess.
    Returns:
        output_text (str): The preprocessed text string.
    """
    text = text.lower()
    temp_text = []
    words = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(words)

    for i, word in enumerate(words):
        if pos_tags[i][1] in verb_codes:
            lemmatized = lemmatizer.lemmatize(word, 'v')
        else:
            lemmatized = lemmatizer.lemmatize(word)
        if lemmatized not in stop_words and lemmatized.isalpha():
            temp_text.append(lemmatized)

    output_text = ' '.join(temp_text)
    output_text = output_text.replace("n't", " not")
    output_text = output_text.replace("'m", " am")
    output_text = output_text.replace("'s", " is")
    output_text = output_text.replace("'re", " are")
    output_text = output_text.replace("'ll", " will")
    output_text = output_text.replace("'ve", " have")
    output_text = output_text.replace("'d", " would")
    return output_text

def data_preprocessor(filename):
    """
    Preprocesses the 'description' column of the input DataFrame.

    Cleans data by:
      • Removing rows with more than two 'empty' entries overall.
      • Replacing empty/'empty' descriptions with their corresponding title.
      • Replacing empty/'empty' supervisor fields or those with >15 words with "parse failed".
    Then tokenizes the description and saves the tokenized CSV.
    """

    import numpy as np

    # Load input CSV
    dataframe = pd.read_csv(f"data/project_CSVs/{filename}")

    # --- Rule 1: remove rows with too many 'empty' entries ---
    def too_many_empties(row):
        text = " ".join(map(str, row.values)).lower()
        return text.count("empty") > 2

    before_count = len(dataframe)
    dataframe = dataframe[~dataframe.apply(too_many_empties, axis=1)].reset_index(drop=True)

    # --- Rule 2: fill empty/'empty' descriptions with title ---
    desc = dataframe["description"].fillna("").astype(str).str.strip()
    empty_desc_mask = (desc == "") | (desc.str.lower() == "empty")
    num_filled = empty_desc_mask.sum()
    if num_filled > 0:
        dataframe.loc[empty_desc_mask, "description"] = dataframe.loc[empty_desc_mask, "title"]
        print(f"Filled {num_filled} empty descriptions with corresponding titles.")

    # --- Rule 3: handle supervisors ---
    sup = dataframe["supervisors"].fillna("").astype(str).str.strip()
    too_long_mask = sup.apply(lambda x: len(x.split()) > 15)
    empty_sup_mask = (sup == "") | (sup.str.lower() == "empty")
    parse_failed_mask = too_long_mask | empty_sup_mask
    num_failed = parse_failed_mask.sum()
    if num_failed > 0:
        dataframe.loc[parse_failed_mask, "supervisors"] = "parse failed"
        print(f"Marked {num_failed} supervisor entries as 'parse failed' (empty or >15 words).")

    # --- Summary of cleanup ---
    after_count = len(dataframe)
    removed = before_count - after_count
    if removed != 0:
        print(f"Removed {removed} rows with too many 'empty' fields.")
    else:
        print("No rows removed for excessive 'empty' fields.")

    # --- Tokenize the description column ---
    dataframe["tokenized_description"] = dataframe["description"].apply(preprocess_text)

    # The output (new) file name
    new_filename = f"tokenized_{filename}"

    # Save to tokenized_CSVs directory
    dataframe.to_csv(f"data/tokenized_CSVs/{new_filename}", index=False)
    print(f"Saved cleaned and tokenized CSV to data/tokenized_CSVs/{new_filename}")


# Previous code to delete rows
# def data_preprocessor(filename):
#     """
#     Preprocesses the 'description' column of the input DataFrame.
#     Args:
#         CSV File (.csv): The project list CSV name from the data/project_CSVs folder.
#     Saves:
#         CSV File (.csv): A new CSV with an additional 'tokenized_description'
#           column in data/tokenized_CSVs folder.
#     Returns:
#         None
#     """
#     # The input (original) file
#     dataframe = pd.read_csv(f'data/project_CSVs/{filename}')
#     def too_many_rows(row):
#         text = " ".join(map(str, row.values)).lower()
#         # Remove row if "empty" appears more than twice
#         return text.count("empty") > 2
#     before_count = len(dataframe)
#     # Drop rows where too_many_rows() is True
#     dataframe = dataframe[~dataframe.apply(too_many_rows, axis=1)]
#     after_count = len(dataframe)
#     if before_count - after_count != 0:
#         print(f"Removed {before_count - after_count} rows containing 'empty' more than twice.")
#     else:
#         print("No need to remove any rows.")
#     # Tokenize the description column
#     dataframe['tokenized_description'] = dataframe['description'].apply(preprocess_text)
#     # The output (new) file name
#     new_filename = f"tokenized_{filename}"
#     # Save to tokenized_CSVs directory
#     dataframe.to_csv(f"data/tokenized_CSVs/{new_filename}", index=False)
def query_preprocessor(query):
    """
    Preprocesses the input query string.
    
    Args:
        query (str): The input query string to preprocess.
    Returns:
        tokenized_query (str): The tokenized query string.
    """
    processed_query = preprocess_text(query)
    return processed_query
