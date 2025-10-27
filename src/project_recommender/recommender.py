# Placeholder for recommender script
# Functionality: (Data.Description) tokenized text + (User Query) tokenized text -> (Recommendations) list of Data.ProjectTitle strings

import pandas as pd

from preprocessor import query_preprocessor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
tfidfvec = TfidfVectorizer()

def recommend(user_input,tokenized_data):
    "Takes a user statement and tokenized_data, and returns the"
    "project title which matches closest to the user statement "

    "Args: User statement (e.g. 'I am James, I'm interested in the studying the pandemic)"
    "and tokenized_data (processed versions of the project descriptions)"

    "Returns: The project title which is 'closest' to the user statement"

    #processes the user statement, removes unnecessary words
    user_tokens = query_preprocessor(user_input)  
    
    #transforms the processed user statement into vectorised form
    tfidf_user = tfidfvec.transform(user_tokens)

    #transforms the processed project descriptions into vectorized form    
    tfidf_data = tfidfvec.fit_transform(tokenized_data['tokenized_description'])

    #creates a score between the user statement and project descriptions based on how similar
    cos_sim = cosine_similarity(tfidf_user, tfidf_data)

    #finds the highest score
    best_score = cos_sim.argmax()

    #returns the title of the project which obtained the highest score
    return tokenized_data['title'][best_score]



