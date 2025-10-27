# Author: Vaideha Sathe
# Date: 27/10/2025 
#--------------------------------------------------------#
# Description: This module contains functions to preprocess text data to feed into the recommender module.
# Functionality: Original Text -> Tokenized Text
# data_preprocessor: Tokenizes all description elements from Extracted Data CSV
# query_preprocessor: Tokenizes input text string for recommender
# NOTE: REQUIRES NLTK DATA TO BE DOWNLOADED. RUN setup_nltk.py IN config FOLDER TO DOWNLOAD.
#--------------------------------------------------------#
import nltk 
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk.corpus import stopwords
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

def data_preprocessor(dataframe):
    """
    Preprocesses the 'description' column of the input DataFrame.
    
    Args:
        dataframe (pd.DataFrame): The input DataFrame with a 'description' column.
    Returns:
        dataframe (pd.DataFrame): The DataFrame with a new preprocessed 'tokenized_description' column.
    """
    dataframe['tokenized_description'] = dataframe['description'].apply(preprocess_text)
    return dataframe

def query_preprocessor(query):
    """
    Preprocesses the input query string.
    
    Args:
        query (str): The input query string to preprocess.
    Returns:
        processed_query (str): The preprocessed query string.
    """
    processed_query = preprocess_text(query)
    return processed_query


