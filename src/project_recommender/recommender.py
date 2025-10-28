# Date 28/10/2025
# DESCRIPTION: This function takes a user input as a string,
# and a .csv file containing tokenized project data,
# and returns a number of projects (decided by the user) which
# are most similar to the user input string

from preprocessor import query_preprocessor
import pandas as pd
import nltk
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
tfidfvec = TfidfVectorizer()

def recommend(user_input,tokenized_data_csv,amount_wanted):
    "Takes a user statement and .csv file, and returns the"
    "project title which matches closest to the user statement "

    "Args: User statement (e.g. 'I am James, I'm interested in the studying the pandemic)"
    "and .csv file containing tokenized data (processed versions of the project descriptions)"

    "Returns: The project title which is 'closest' to the user statement"
    
    #check that the user input is greater than 15 words
    if len(user_input.split())<=15:
        return "Your statement is too short!"
    else:

        #read the .csv file
        tokenized_data = pd.read_csv(tokenized_data_csv)

        #processes the user statement, removes unnecessary words
        user_tokens = query_preprocessor(user_input)  

        #transforms the processed project descriptions into vectorized form    
        tfidf_data = tfidfvec.fit_transform(tokenized_data['tokenized_description'])

        #turn user_tokens into a list which transform will accept
        user_tokens_list = user_tokens.split(" ")

        #transforms the processed user statement into vectorised form
        tfidf_user = tfidfvec.transform(user_tokens_list)

        #creates a score between the user statement and project descriptions based on how similar
        cos_sim = cosine_similarity(tfidf_user, tfidf_data)

        #adds the scores for each project
        project_scores = np.sum(cos_sim, axis=0)

        #lists the indices from highest-to-lowest score
        indices_sorted = np.argsort(project_scores)[::-1]
        no_zeros = indices_sorted[project_scores[indices_sorted]>0]
        
        #keeps the number of amount_wanted
        no_zeros_correct_amount=no_zeros[:amount_wanted]

        #adds those projects to a list
        projects=[]
        for i in no_zeros_correct_amount:
            projects.append([tokenized_data['title'][i],project_scores[i]])
        
        #if the user wanted more than were suggested
        if len(projects)<amount_wanted:
            print('There are only',len(projects),'recommendations: ')
        
        #change formatting
        final_projects=np.array(projects)

        return final_projects