from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import urllib.parse
import nltk
#nltk.download('punkt')
from nltk import sent_tokenize
from nltk.stem import PorterStemmer
from collections import defaultdict
import string
import numpy as np
import re
import math
import requests
from pymongo import MongoClient
import pandas as pd
import spacy
from nltk.corpus import stopwords
stop = stopwords.words('english')
#load the pre-trained NER model
nlp = spacy.load('en_core_web_sm')

#Connect to mongo db server
#Mongodb server now hosted on the cloud
def connectMongo():
    try:
        client = MongoClient('mongodb://root:roots3creT@ec2-34-243-142-86.eu-west-1.compute.amazonaws.com:27017')
        print('Connected successfully')
    except:
        print('Could not connect to database')
        return None
    else:
        return client

#
def insertInMongo(url, ner_tags, text):
    #a dictionary for data entry
    doc = {}
    words = []
    doc_tokens = []
    uniq_word = []
    doc['url'] = url
    #store all the unique words in the document along with its NER tag
    for word, tag in ner_tags:
        if word not in uniq_word:
            token = {}
            count = 0
            token['word'] = word
            if tag == '':
                token['label'] = 'UNLBL' #unlabelled
            else:
                token['label'] = tag
                
            #get the number of mentions
            for w, t in ner_tags:
                if word == w:
                    count += 1
            token['count'] = count
            doc_tokens.append(token)
            uniq_word.append(word)
            
    doc['tokens'] = doc_tokens
    doc['text'] = text
  
    client = connectMongo()
  
    if client!=None:
        #Switch to the database where we want to store the collections/tables
        db = client['ner_db']
        
        #switch to collection
        collection = db['doc_ner']
    
        try:
            rec = collection.insert(doc)
            print('Insertion Complete')
        except PyMongoError as mongo_err:
            print('Could not insert into collection' )
    else:
        print('Cannot connect to Mongo')

#REFERENCE:https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
#perform webscraping
def scrapeUrls(urls):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    docs_text = []
    scraped_urls = []
    for u in urls:
        try:
            req = urllib.request.Request(url=u, headers=headers)
            html = urllib.request.urlopen(req)
            soup = BeautifulSoup(html.read(), 'html.parser')
            #return all text within <p> tags
            text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
            sentences = nltk.tokenize.sent_tokenize(text)
            #Pre-processing: remove escape characters from sentences
            processed_sentences = [re.sub(r'\s+', ' ', sent) for sent in sentences]
            main_text = ' '.join(processed_sentences)
            if main_text != '':
                #get the body of the webpage and append it to the array
                docs_text.append(main_text) 
        except:
            print('Failed to scrape web page')
    return docs_text

def insertTaggedText(urls,docs_text):
    #apply NER
    for i in range(len(docs_text)):
        tagged_words = []
        try:
            if UrlExist(urls[i]) == False:
                nlp_text = nlp(docs_text[i])
                word_tag_pairs = [(str(X), X.ent_type_) for X in nlp_text]

                for word, tag in word_tag_pairs:
                    #get all the unique words that are tagged by NER
                    #Pre-processing:Ignore stop words
                    if word not in stop and word not in string.punctuation and not word.isdigit():
                        for w, t in tagged_words:
                            if word == w and tag != t:
                                tag = t
                        tagged_words.append((word,tag))
                insertInMongo(urls[i],tagged_words, docs_text[i]) 
            else:
                print('Article already inserted in database')
                continue
        except:
            continue

#main function
def loadData(batch_path):
    #fetch the urls from file
    f1 = open(batch_path)
    batch = f1.readlines()
    #remove newline character at the end of each URLs
    file_urls = [u.strip('\n') for u in batch]
    
    #scrape main text from urls and store in Mongo
    docs_text = scrapeUrls(file_urls)
    insertTaggedText(file_urls,docs_text)
    f1.close()
