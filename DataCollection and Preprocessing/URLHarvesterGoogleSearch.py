# Import statements
from googlesearch import search
import pandas as pd
import pathlib

# Function that performs a google search and returns URLs.
def googleSearchFunction(ent, keyW):
    urlsList = list()
    
    # Can't make too many or too frequent calls of the IP address get blocked by Google
    query = ent + " " + keyW
    for url in search(query, tld='com', lang='en', start=0, stop=400, pause=15):
        print(url)
        if url not in urlsList:
            urlsList.append(url)
            
    urlToFile(urlsList)

# Function that converts the URLs gathered by googleSearchFunction() to a file.
def urlToFile(listOfUrls):  
    urlsFromFile = list()
    urlsToAppend = list()
    
    file = pathlib.Path("urls.txt")
    if file.exists():
        # Reading each line from the existing URLs file into a list.
        urlsFromFile = [line.rstrip('\n') for line in open('urls.txt')]
    
        # Checking is URL already exists in the file.
        # If it does, it is ignored and the next url is checked.
        # If the URl is not already in the file it is added to the list.
        for url in listOfUrls:
            if url not in urlsFromFile:
                urlsToAppend.append(url)
    
        # Converting the list to the dataframe for easier writing to files.
        urlDataframe = {'Url':urlsToAppend}
        df = pd.DataFrame(urlDataframe)
        
		# Opening the file to which the URLs are to be appended.
		# The file is opened in write mode so that all previous data in it is overwritten.
		# Doing this makes sure that when the data extractor is run on the file, no duplicates are entered into the database.
		with open("urls.txt", "w") as filePointer:
			df.to_csv(filePointer, header = False, index = False)
			filePointer.close()
    else:
        # Converting the list passed as a parameter to the function into a dataframe.
        urlDataFrame = {'Url':listOfUrls}
        df = pd.DataFrame(urlDataFrame)
        
        # Creating a new file.
        with open("urls.txt", "w") as filePointer:
            df.to_csv(filePointer, header = False, index = False)
            filePointer.close()


# Keywords (Environmental Topics) and Entities (Companies).
entities = ['microsoft', 'google', 'facebook', 'toyota', 'apple', 'dell', 'cisco', 'tesco', 'tesla', 'amazon']
keywords = ['green energy', 'recycling', 'climate change', 'solar power', 'sustainability', 'renewable', 'bio energy', 'biomass', 'carbon footprint', 'wind farm']


# looping through each of the elements of the lists and passing them to googleSearchFunction() to form the query.
for entity in entities:
    for keyword in keywords:
        googleSearchFunction(entity, keyword)

# Importing the DataExtractor module
from DataExtractor import loadData

# Executing the DataExtractor on the news_urls.txt file
loadData("urls.txt")

