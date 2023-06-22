# PROGRAMMER: Nathan Vuong

# IMPORTS
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import praw
import prawcore
import sqlite3
from tables import Database, TermFrequency, TFIDF, numOfEntries

def fillDatabases(targetCommunity):
    # Create tables
    indexConnection = sqlite3.connect("database.db")
    index = Database(indexConnection)
    index.createTable()
    frequencyConnection = sqlite3.connect("termFrequency.db")
    frequency = TermFrequency(frequencyConnection)
    frequency.createTable()
    
    # API setup
    user_agent = "Scraper 1.0 by /u/organic_browser"
    reddit = praw.Reddit(
        client_id = "Placeholder",
        client_secret = "Placeholder",
        user_agent = user_agent
    )

    # Add entries to database and positional index dictionary
    # Limit to 50 entries b/c slow computer
    docID = 0
    try:
        for submission in reddit.subreddit(targetCommunity).hot(limit = None):
            # For database
            newEntry = [docID, submission.title, submission.url, submission.author.name, str(submission.created_utc), submission.score]
            index.addEntry(newEntry)
            # Clean titles, tokenize, remove stop words, and lemmatize
            lemmatizer = WordNetLemmatizer()
            stopWords = stopwords.words("english")
            cleanTitle = re.sub(r'[^\w\s]', '', submission.title)
            cleanTitle = cleanTitle.lower()
            words = nltk.word_tokenize(cleanTitle)
            filteredWords = [w for w in words if not w in stopWords]
            # Add entries to term frequency database
            frequency.addEntry(filteredWords, docID)
            docID += 1
            if (docID == numOfEntries):
                break
    # Raise error if subreddit cannot be reached
    except (prawcore.exceptions.NotFound, prawcore.exceptions.Forbidden) as error:
        raise LookupError("Subreddit does not exist!")
    # Build TFIDF database based on term frequency database
    tfidfConnection = sqlite3.connect("tfidf.db")
    tfidf = TFIDF(tfidfConnection)
    tfidf.createTFIDF()