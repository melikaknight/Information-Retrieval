from hazm import *

def stemming(word,isnaun=False):
    if isnaun:
        stemmer = Stemmer()
        return(stemmer.stem(word))
    else:
        lemmatizer = Lemmatizer()
        return(lemmatizer.lemmatize(word))
