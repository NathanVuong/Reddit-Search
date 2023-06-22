# PROGRAMMER: Nathan Vuong

# IMPORTS
import tkinter as tk
import ttkbootstrap as ttk
from fill_tables import fillDatabases
from query import topSearches
import sqlite3
from tables import Database
import webbrowser

# Clear window
def clearFrame(frame):
    for item in frame.winfo_children():
        item.destroy()

# Class for gui
class SearchApplication():
    def __init__(self):
        self.__root = ttk.Window()
        width = self.__root.winfo_screenwidth()
        height = self.__root.winfo_screenheight()
        self.__root.geometry("%dx%d" % (width, height))
        self.__root.title("Reddit Search")
        self.__masterFrame = tk.Frame(self.__root)
        self.__masterFrame.pack(fill = "both", expand = True)
    
    # First window will ask the user to choose a subreddit
    def createSubredditSearch(self):
        # Make sure there is nothing in the frame
        clearFrame(self.__masterFrame)

        # Labels
        titleLabel = ttk.Label(master = self.__masterFrame, text = "Reddit Search", font = "Calibri 24 bold")
        titleLabel.pack()
        subredditLabel = ttk.Label(master = self.__masterFrame, text = "Enter the subreddit to search:", font = "Calibri 20")
        subredditLabel.pack()
        subredditFrame = ttk.Frame(master = self.__masterFrame)
        subredditFrame.pack(pady = 10)
        subredditString = tk.StringVar()
        subredditEntry = ttk.Entry(master = subredditFrame, textvariable = subredditString)
        subredditEntry.pack(side = "left", padx = 10)
        
        # Display whether or not subreddit is valid
        errorFrame = ttk.Frame(master = self.__masterFrame)
        errorFrame.pack()

        # Command when subreddit is entered
        def getSubreddit():
            clearFrame(errorFrame)
            try:
                fillDatabases(subredditString.get())
                SearchApplication.createRedditSearch(self)
            except Exception as error:
                errorLabel = ttk.Label(master = errorFrame, text = "Oops! It seems r/" + subredditString.get() + " does not exist or you do not have permission to access it!", font = "Calibri 20")
                errorLabel.pack()
        
        subredditEnterButton = ttk.Button(master = subredditFrame, text = "Enter", command = getSubreddit)
        subredditEnterButton.pack(side = "left")

    # Once subreddit has been selected, change window
    def createRedditSearch(self):
        # Make sure there is nothing in the frame
        clearFrame(self.__masterFrame)

        # Create table
        titleLabel = ttk.Label(master = self.__masterFrame, text = "Reddit Search", font = "Calibri 24 bold")
        titleLabel.pack()
        queryLabel = ttk.Label(master = self.__masterFrame, text = "Enter the query:", font = "Calibri 20")
        queryLabel.pack()
        queryFrame = ttk.Frame(master = self.__masterFrame)
        queryFrame.pack(pady = 10)
        queryString = tk.StringVar()
        subredditEntry = ttk.Entry(master = queryFrame, textvariable = queryString)
        subredditEntry.pack(side = "left", padx = 10)

        # Go back to search different subreddit
        def goBack():
            SearchApplication.createSubredditSearch(self)
        goBackButton = ttk.Button(master = self.__masterFrame, text = "Go Back", command = goBack)
        goBackButton.pack(pady = 20)

        # Space for results
        resultsFrame = ttk.Frame(master = self.__masterFrame)
        resultsFrame.pack(fill = "both", expand = True)

        def wrap(string):
            if len(string) > 65:
                string = string[0:64] + "..."
            return string
        
        # Command when query is inputted
        def getResults():
            # Clear previous searches
            clearFrame(resultsFrame)

            # Given the query return the top results
            champions = topSearches(queryString.get())
            if (len(champions) == 0):
                noResultsLabel = ttk.Label(resultsFrame, text = "No matches found...", font = "Calibri 16 bold")
                noResultsLabel.pack()
            else:
                # Create treeview
                table = ttk.Treeview(resultsFrame, bootstyle = "success", columns = ("Description", "Author", "Upvotes", "Date", "Link"), show = "headings", selectmode = "browse")
                table.column("# 1", width = 500)
                table.heading("Description", text = "Description")
                table.heading("Author", text = "Author")
                table.heading("Upvotes", text = "Upvotes")
                table.heading("Date", text = "Date")
                table.heading("Link", text = "Link")
                table.pack(side = "left", fill = 'both', expand = True, padx = 5, pady = 5)
                # Create scrollbar
                scrollbar = ttk.Scrollbar(resultsFrame, orient = "vertical", command = table.yview)
                scrollbar.pack(side = "right", fill = "y")
                table.configure(xscrollcommand = scrollbar.set)
                # Database connection
                databaseConnection = sqlite3.connect("database.db")
                database = Database(databaseConnection)
                # Function for accessing hyperlink
                def openLink(event):
                    tree = event.widget  
                    item = tree.item(tree.focus())
                    link = item["values"][4]
                    webbrowser.open_new_tab(link)
                # Displaying results
                for champion in champions:
                    results = database.getEntryByID(champion)
                    table.insert(parent = "", index = ttk.END, values = (wrap(results[1]), results[3], results[5], results[4], results[2]))
                    table.bind("<<TreeviewSelect>>", openLink)
                    
        subredditEnterButton = ttk.Button(master = queryFrame, text = "Search", command = getResults)
        subredditEnterButton.pack(side = "left")

    # Get the main window
    def getApplicationWindow(self):
        return self.__root

# Main
def main():
    searchWindow = SearchApplication()
    searchWindow.createSubredditSearch()
    searchWindow.getApplicationWindow().mainloop()
    
main()