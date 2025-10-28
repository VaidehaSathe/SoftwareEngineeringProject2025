# NEEDS TO BE MADE PROPERLY WITH PYTEST FRAMEWORK LATER

import os
import sys
# Put the project's src/ directory on sys.path so `project_recommender` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_data_preprocessor():
    import pandas as pd
    from project_recommender.preprocessor import data_preprocessor
    df = pd.read_csv("src/project_recommender/parsed.csv")
    processed_df = data_preprocessor(df)
    print(processed_df[['description', 'tokenized_description']].head())
    processed_df.to_csv('data/preprocessor_mock-data/tokenized_parsed.csv', index=False)   

test_data_preprocessor()