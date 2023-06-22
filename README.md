# Reddit-Search
Simple Reddit search engine created using Python with various Python libraries, TF-IDF weighting, and the Reddit API.

To use this program, create a Reddit API account in order to get a client id and a secret id. Use these values in the fill_tables.py file to replace the variables set equal to the default value "Placeholder."

The global variable numOfEntries found in the tables.py files can be set to larger or smaller numbers, however creating more indexes will lead to a longer runtime.

When ready to run, run the gui.py file to see the user interface. The user will be prompted to enter the name of the subreddit, and once received, the program will begin indexing the entries. Once completed, the user can enter queries to see the most relavent results.
