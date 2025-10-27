# NEEDS TO BE MADE PROPERLY WITH PYTEST FRAMEWORK LATER

def test_data_preprocessor():
    import pandas as pd
    from project_recommender.preprocessor import data_preprocessor
    df = pd.read_csv('data/preprocessor_mock-data/books_mock_data.csv')
    processed_df = data_preprocessor(df)
    print(processed_df[['description', 'tokenized_description']].head())
    processed_df.to_csv('data/preprocessor_mock-data/books_tokenized_mock_data.csv', index=False)   