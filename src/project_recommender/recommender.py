# Date 28/10/2025
# DESCRIPTION: This function takes a user input as a string,
# and a .csv file containing tokenized project data,
# and returns a number of projects (decided by the user) which
# are most similar to the user input string


# Added file handling with Path from pathlib/

from preprocessor import query_preprocessor
import pandas as pd
import nltk
import numpy as np
from pathlib import Path

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


# If this file is located at src/projects_recommend/..., then:
HERE = Path(__file__).resolve().parent           # src/projects_recommend
PROJECT_ROOT = HERE.parent.parent                 # project_root

def resolve_data_path(path_like: str) -> Path:
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

#  [['A53 Uncovering novel microglial biology through high-content microscopy by developing CellPainting pipelines'
#   '0.541533439982456']
#  ['A5 Developing viral dynamics models for optimising vaccination production'
#   '0.48694152098311627']
#  ['A60 Dynamic adaptation of plasma cell differentiation in complex environments'
#   '0.3481370902999725']
#  ['A35 Decoding the Human Gut Immune Landscape Through Single-Cell Profiling'
#   '0.3458495851515635']
#  ['A48 Structural mechanisms of T cell receptor recognition of peptide antigen through pMHC complexes'
#   '0.3428799153782547']
#  ['A4 Investigating the impact of microbiome variation on the T cell repertoire in immunity and inflammation'
#   '0.3071470647906721']
#  ['A22 Which cytoskeletal proteins organise the malaria parasite and how do they work?'
#   '0.30317572393105974']
#  ['A17 Molecular mechanisms underlying viral evolution and host changes'
#   '0.2917387837169717']
#  ['A46 Extracellular Sphingolipids as Drivers and Modulators of Endothelial Vesicle Function in Health'
#   '0.28651838111994676']
#  ['A57 Using super-resolution microscopy to understand how pathogenic bacteria survive antibiotics and immune defences'
#   '0.2713573986329264']]

# projs = recommend(
#     "I want to know about biology cell movement and use machine learning with python for mathematical modelling", 
#     tokenized_data_csv=resolve_data_path("tokenized_projects_summary.csv"),
#     amount_wanted=10)

# print(projs)
