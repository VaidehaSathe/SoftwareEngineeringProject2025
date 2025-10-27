## Downloads all requried attributes of the NLTK library.

import nltk

resources = ['punkt', 'averaged_perceptron_tagger', 'wordnet', 'stopwords']

for resource in resources:
    nltk.download(resource)
