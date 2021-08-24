# Import statements.
import pandas as pd
# GoogleNews package by Hurin Hu.
from GoogleNews import GoogleNews


# Function that takes an entity and keyword as inputs and forms a query using them.
# The query is then passed to "search" function for GoogleNews.
# These are then passed to a function that stores them in a file.
def googleNewsScraper(ent, keyW):
    googlenews = GoogleNews()

    news_urls = list()
    
    # Creating a query string by combining keywords and entities
    query = ent + " " + keyW
    googlenews.search(query)
    news = googlenews.getlinks()

    news_urls.append(news)
    urls_list = list()
    for url in news_urls[0]:
        urls_list.append(url)
        
    print(urls_list)
        
    urlToFile(urls_list)


# Function that stores the URLs returned by googleNewsScraper() into a text file.
def urlToFile(listOfUrls):
    # Reading each line from the existing URLs file into a list.
    urlsFromFile = list()
    urlsToAppend = list()
	
	file = pathlib.Path("news_urls.txt")
    if file.exists():
		# Reading each line from the existing URLs file into a list.
		urlsFromFile = [line.rstrip('\n') for line in open('news_urls.txt')]
    
		# Checking is URL already exists in the file.
		# If it does, it is ignored and the next url is checked.
		# If the URl is not already in the file
		for url in listOfUrls:
			if url not in urlsFromFile:
				urlsToAppend.append(url)
    
		# Converting the list to the dataframe for easier writing to files.
		urlDataframe = {'Url':urlsToAppend}
		df = pd.DataFrame(urlDataframe)
		
		# Opening the file to which the URLs are to be appended.
		# The file is opened in write mode so that all previous data in it is overwritten.
		# Doing this makes sure that when the data extractor is run on the file, no duplicates are entered into the database.
		with open("news_urls.txt", "w") as filePointer:
			df.to_csv(filePointer, header = False, index = False)
			filePointer.close()
	else:
        # Converting the list passed as a parameter to the function into a dataframe.
        urlDataFrame = {'Url':listOfUrls}
        df = pd.DataFrame(urlDataFrame)
        
        # Creating a new file.
        with open("news_urls.txt", "w") as filePointer:
            df.to_csv(filePointer, header = False, index = False)
            filePointer.close()


# Keywords (Environmental Topics) and Entities (Company names).
entities = ['microsoft', 'google', 'facebook', 'toyota', 'apple', 'dell', 'cisco', 'tesco', 'tesla', 'amazon']
keywords = ['green energy', 'recycling', 'climate change', 'solar power', 'sustainability', 'renewable', 'bio energy', 'biomass', 'carbon footprint', 'wind farm']


# Passing the keywords and entities to the googleNewsScraper().
for entity in entities:
    for keyword in keywords:
        googleNewsScraper(entity, keyword)
		
# Importing the DataExtractor module
from DataExtractor import loadData

# Executing the DataExtractor on the news_urls.txt file
loadData("news_urls.txt")