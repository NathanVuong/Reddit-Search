# PROGRAMMER: Nathan Vuong

# IMPORTS
import sqlite3
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from tables import TermFrequency, TFIDF, numOfEntries
from math import log10
import re

# Convert query into TFIDF vector
def vectorizeQuery(query):
    # Connect to term frequency database
    connection = sqlite3.connect("termFrequency.db")
    cursor = connection.cursor()
    frequency = TermFrequency(connection)
    # Find all terms
    terms = frequency.getTerms()
    terms = [''.join(i) for i in terms]
    # Tokenize the query
    lemmatizer = WordNetLemmatizer()
    stopWords = stopwords.words("english")
    cleanQuery = re.sub(r'[^\w\s]', '', query)
    cleanQuery = cleanQuery.lower()
    queryWords = nltk.word_tokenize(cleanQuery)
    queryWords = [w for w in queryWords if not w in stopWords]
    # Create TFIDF vector and begin to fill it
    returnVector = []
    for term in terms:
        if term in queryWords:
            tf = (1 + log10(queryWords.count(term) / len(queryWords)))
            occurences = frequency.getOccurencesByTerm(term)
            idf = log10(numOfEntries / occurences[0])
            returnVector.append(tf * idf)
        else:
            returnVector.append(0.0)
    return returnVector

# Returns dot product (similarity)
def cosineTFIDFSimilarity(queryOne, queryTwo):
    cos = np.dot(queryOne, queryTwo)
    return cos

# Return organized list of top k results given user query
def topSearches(userQuery):
    connection = sqlite3.connect("tfidf.db")
    cursor = connection.cursor()
    tfidf = TFIDF(connection)

    # Create dictionary with search results and fill it
    searchResults = {}
    
    for i in range(numOfEntries):
        queryOne = vectorizeQuery(userQuery)
        queryTwo = tfidf.getTFIDF(i)
        searchResults[i] = cosineTFIDFSimilarity(queryOne, queryTwo)

    # Sort all relevant entries (entries that have a dot product > 0)
    sortedResults = []
    for i in range(numOfEntries):
        if max(searchResults, key=searchResults.get) == 0.0:
            break
        sortedResults.append(max(searchResults, key=searchResults.get))
        searchResults.pop(sortedResults[i])
    return sortedResults