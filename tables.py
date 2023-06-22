# PROGRAMMER: Nathan Vuong

# IMPORTS
import sqlite3
import datetime
from math import log10

# Variable will contain the number of indexes created per search
# More indexes will lead to more results but a longer indexing time
numOfEntries = 50

# Parent table class
class Table:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.conn = connection
        self.c = connection.cursor()

# Database that will hold information about each post inside
class Database(Table):
    
    # If database doesn't already exist create it
    # If database already exists delete it and create a new one
    def createTable(self):
        self.c.execute("DROP TABLE IF EXISTS database")
        self.c.execute("CREATE TABLE database(id INTEGER NOT NULL PRIMARY KEY,\
            title TEXT NOT NULL, url TEXT NOT NULL, author TEXT,\
            date TEXT NOT NULL, upvotes INTEGER NOT NULL)")

    # Receive list describing an entry and enter into database
    def addEntry(self, entry):
        entry[4] = datetime.datetime.fromtimestamp(float(entry[4]))
        self.c.execute("INSERT OR REPLACE INTO database VALUES(:id, :title, :url, :author, :date, :upvotes)", 
        {"id": entry[0], "title": entry[1], "url": entry[2], "author": entry[3], "date": entry[4], "upvotes": entry[5]})
        self.conn.commit()
    
    # Return data entry given an id
    def getEntryByID(self, id):
        entry = self.c.execute("SELECT * FROM database WHERE id = " + str(id)).fetchall()
        return entry[0]

# Database that will hold term frequency information
class TermFrequency(Table):
    # If database doesn't already exist create it
    # If database already exists delete it and create a new one
    # Database will store the term, number of documents containing the term, and the postings
    # Postings are in the format docID : Frequency of term;
    def createTable(self):
        self.c.execute("DROP TABLE IF EXISTS termFrequency")
        self.c.execute("CREATE TABLE termFrequency(term TEXT NOT NULL PRIMARY KEY, occurences INT, postings TEXT)")
    
    # Entry will come in as a tokenized list with docID
    def addEntry(self, entry, docID):
        # Build dictionary with number of occurences of terms
        occurenceDictionary = {}
        for word in entry:
            if word in occurenceDictionary:
                occurenceDictionary[word] += 1
            else:
                occurenceDictionary[word] = 1
        # Begin filling in database
        for key in occurenceDictionary:
            # existsInDatabase will be None if the term is not already in database
            self.c.execute("SELECT * FROM termFrequency WHERE term = :term", {"term": key})
            existsInDatabase = self.c.fetchone()
            # print(existsInDatabase)
            # Update database
            if existsInDatabase != None:
                #self.c.execute("UPDATE termFrequency SET occurences = occurences + 1 WHERE term = '" + key + "'")
                self.c.execute("UPDATE termFrequency SET occurences = 1 WHERE term = '" + key + "'")
                newPosting = f" {docID} : {str(occurenceDictionary[key])}/{str(len(occurenceDictionary))};"
                self.c.execute("UPDATE termFrequency SET postings = postings || :newPosting WHERE term = '" + key + "'", {"newPosting": newPosting})
            else:
                self.c.execute("INSERT INTO termFrequency VALUES(:term, :occurences, :posting)",
                           {"term": key, "occurences": str(occurenceDictionary[key]), "posting": f"{docID} : {str(occurenceDictionary[key])}/{str(len(occurenceDictionary))};"})
            self.conn.commit()

    # Return data entry given by term
    def getEntryByTerm(self, term):
        self.c.execute("SELECT postings FROM termFrequency WHERE term = :term",
                       {"term": term})
        output = self.c.fetchone()
        return output
    
    # Return occurences of term throughout documents
    def getOccurencesByTerm(self, term):
        self.c.execute("SELECT occurences FROM termFrequency WHERE term = :term",
                       {"term": term})
        output = self.c.fetchone()
        return output

    # Return terms
    def getTerms(self):
        self.c.execute("SELECT term FROM termFrequency")
        output = self.c.fetchall()
        return output

class TFIDF(Table):
    # Create TFIDF table
    # Table will be in the format docID : TFIDF
    def createTFIDF(self):
        # Build initial TFIDF table
        self.c.execute("DROP TABLE IF EXISTS tfidf")
        self.c.execute("CREATE TABLE tfidf(docID INT NOT NULL PRIMARY KEY, tfidf_vector TEXT)")
        for docID in range(0, numOfEntries):
            self.c.execute("INSERT INTO tfidf VALUES(:docID, :tfidf_vector)",
            {"docID": docID, "tfidf_vector": ""})
        # Make connection to term frequency database
        frequencyConnection = sqlite3.connect("termFrequency.db")
        frequency = TermFrequency(frequencyConnection)
        # Begin filling in TFIDF values
        terms = frequency.getTerms()
        for term in terms:
            containsTerm = []
            df = frequency.getEntryByTerm(term[0])[0].split("; ")
            df[len(df) - 1] = df[len(df) - 1][:-1]
            for i in range(0, len(df)):
                id = df[i].split(" : ")[0]
                containsTerm.append(int(id))
                operands = df[i].split(" : ")[1].split("/")
                tf = log10(float(operands[0])/float(operands[1]) + 1)
                idf = log10(numOfEntries/len(df))
                tfidf = tf * idf
                newPosting = str(tfidf) + " "
                self.c.execute("UPDATE tfidf SET tfidf_vector = tfidf_vector || :newPosting WHERE docID = '" + str(id) + "'", {"newPosting": newPosting})
            for i in range(0, numOfEntries):
                if i not in containsTerm:
                    self.c.execute("UPDATE tfidf SET tfidf_vector = tfidf_vector || '0 ' WHERE docID = '" + str(i) + "'")
        self.conn.commit()
    
    # Returns TFIDF as a string by docID
    def getTFIDF(self, docID):
        self.c.execute("SELECT tfidf_vector FROM tfidf WHERE docID = :docID",
                            {"docID": docID})
        output = self.c.fetchone()
        output = ''.join(output)
        output = output.split(" ")[:-1]
        output = [float(value) for value in output]
        return output