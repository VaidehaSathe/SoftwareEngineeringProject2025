# NEEDS TO BE MADE PROPERLY WITH PYTEST FRAMEWORK LATER

def test_data_preprocessor():
    import pandas as pd
    from project_recommender.preprocessor import data_preprocessor
    df = pd.read_csv("src/project_recommender/parsed.csv")
    processed_df = data_preprocessor(df)
    print(processed_df[['Description', 'tokenized_description']].head())
    processed_df.to_csv('data/preprocessor_mock-data/tokenized_parsed.csv', index=False)   

test_data_preprocessor()