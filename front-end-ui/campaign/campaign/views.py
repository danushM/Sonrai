from django.http import HttpResponse
from django.shortcuts import render, render_to_response
import re
import pandas as pd
from collections import defaultdict
from pymongo import MongoClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Bokeh modules
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import Range1d, ResetTool, SaveTool, HoverTool, LabelSet
from bokeh.transform import factor_cmap
from bokeh.palettes import Magma10
from bokeh.core.properties import value

#Initialize the VADER sentiment analyzer
analyser = SentimentIntensityAnalyzer()

# Database Initialization
client = MongoClient('mongodb://root:roots3creT@localhost:27017')
# Mongo Database
db = client.ner_db
# Mongo collection
collection = db.doc_ner

# Homepage view
def homepage(request):
    return render(request,'homepage.html')

# Help page view
def about(request):
    return render(request,'help.html')

# Function to fetch the URLs from MongoDB that match the keyword and company
def getCompanyKeywordHits(company, keyword):
    urls = []
        
    if client!=None:
        # If the keyword has more than one word, for example: Green Energy
        if len(keyword.split(' ')) > 1:
            words = keyword.split()
            query = {"tokens.word": {'$all': [re.compile('^' + words[0] + '$', re.IGNORECASE), re.compile('^' + words[1] + '$', re.IGNORECASE), company]}}
        else:
            # Keywords with the single word
            query = {"tokens.word": {'$all': [re.compile('^' + keyword + '$', re.IGNORECASE), company]}}
        cursor = collection.find(query,{'_id':0, 'url':1})
        #get the counts for each ORG word in the doc
        for res in cursor:
            urls.append(res['url'])
        return urls

# Function to fetch the whole text of urls passed
def getSavedText(urls):
    #iterate through data frame and get the main text of returned urls
    hit_text = []
    for url in urls:
        query = {"url":url}
        cursor = collection.find(query,{'_id':0, 'text':1})
        for res in cursor:
            hit_text.append(res['text'])
    return hit_text

# Function to calculate the sentiment of keyword and company combination for the passed text
# Here the sentiment_range denotes how many lines should be looked into after the match for the sentiment calculation.

def calculateSentiment(text,keyword,company, sentiment_range=1):
   score = 0 # get the sentiment score
   count = 0 #get the average
   #list of sentences
   sent = text.split('.')
   for i in range(len(sent)):
       if company in sent[i] and keyword in sent[i]:
           pos = 0
           if i == 0:
               while pos <= sentiment_range:
                   if (i+pos) < (len(sent) - 1):
                       score += analyser.polarity_scores(sent[pos])['compound']
                       count += 1
                   pos += 1
           elif i == (len(sent) - 1):
               while pos <= sentiment_range:
                   if (i-pos) > 0:
                       score += analyser.polarity_scores(sent[i-pos])['compound']
                       count += 1
                   pos += 1
           else:
               #get the sentiment score for the 'match sentence' i.e. with both keyword and company mentions
               score += analyser.polarity_scores(sent[i])['compound']
               count += 1
               pos += 1
               #get the sentiment score for sentences before 'match sentence' and within sentiment_range
               while pos <= sentiment_range:
                   if (i-pos) > 0:
                       score += analyser.polarity_scores(sent[i-pos])['compound']
                       count += 1
                   pos += 1
               #get the sentiment score for sentences after 'match sentence' and within sentiment_range
               pos = 1
               while pos <= sentiment_range:
                   if (i+pos) < (len(sent) - 1):
                       score += analyser.polarity_scores(sent[i+pos])['compound']
                       count += 1
                   pos += 1
   if count > 0:
       return (score / count)
   return 0

#Results page view
def action(request):
    # Save the query string
    query_dict = request.GET
    # Save the list of selected keywords
    keywords = request.GET.getlist('resource_checkbox')
    # Save the list of selected companies
    entities = request.GET.getlist('company_checkbox')

    # Convert the keywords to lower case as MongoDB search fails with Upper case
    newKeywords = []
    for keyword in keywords:
        newKeywords.append(keyword.lower())
    keywords = newKeywords

    # Convert the first letter of the keyword to upper case, these are used for title of the individual graphs
    tempKeywords = []
    for keyword in keywords:
        tempKeywords.append(keyword.title())
    capitalizeKeywords = tempKeywords

    # Adjust the width of graphs based on number of companies chosen as Bokeh doesn't adjust the width of the bars automatically
    length_entities = len(entities)
    if length_entities < 2 :
        width = 0.1
    elif length_entities < 3:
        width = 0.2
    elif length_entities < 4:
        width = 0.3
    elif length_entities < 5:
        width = 0.4
    elif length_entities < 6:
        width = 0.5
    elif length_entities < 7:
        width = 0.6
    elif length_entities < 8:
        width = 0.7
    elif length_entities < 9:
        width = 0.8
    else:
        width = 0.9

    # Colors for the stacked bar graph
    length_keywords = len(keywords)
    if length_keywords == 1:
        colors = [ '#440154' ]
    elif length_keywords == 2:
        colors = [ '#000003', '#FDE724']
    elif length_keywords == 3:
        colors = [ '#000003', '#FDE724', '#430F75']
    elif length_keywords == 4:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81']
    elif length_keywords == 5:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81', '#9E2E7E']
    elif length_keywords == 6:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81', '#9E2E7E', '#CB3E71']
    elif length_keywords == 7:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81', '#9E2E7E', '#CB3E71', '#F0605D']
    elif length_keywords == 8:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81', '#9E2E7E', '#CB3E71', '#F0605D', '#FC9366']
    elif length_keywords == 9:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81', '#9E2E7E', '#CB3E71', '#F0605D', '#FC9366', '#FEC78B']
    else:
        colors = [ '#000003', '#FDE724', '#430F75', '#711F81', '#9E2E7E', '#CB3E71', '#F0605D', '#FC9366', '#FEC78B', '#FBFCBF']

    # Initialize a dataframe, which will hold the chosen companies and sentiment scores for chosen keywords
    df = pd.DataFrame()
    #yogi#log_df = defaultdict(list)

    # Insert the chosen companies into data frame
    df["entity"] = entities

    # Initialize the Bokeh compenenets
    script = []
    div = []
    images = []

    # Create a data frame to store the score for the chosen keywords and companies
    # Loop through the choosen keywords, and find out the score for each company against the keyword

    for keyword in keywords:
        sentiment_scores = []
        #Initial variables
        total_pos = []
        total_neg = []
        total = []
        for company in entities:
            urls = getCompanyKeywordHits(company, keyword)
            sum_score = 0
            sentiment = 0
            total_doc = 0
            pos_count = 0
            neg_count = 0
            if len(urls) > 0:
                url_text = getSavedText(urls)
                total_doc = len(url_text)
                for text in url_text:
                    article_sentiment = calculateSentiment(text,keyword,company,1)
                    sum_score += article_sentiment
                    if article_sentiment > 0:
                        #increment positive count
                        pos_count += 1
                    elif article_sentiment < 0:
                        #increment negative count
                        neg_count += 1
                sentiment = sum_score / len(url_text)
            sentiment_scores.append(sentiment)
            total.append(total_doc)
            total_pos.append(pos_count)
            total_neg.append(neg_count)
        # Insert the sentiment score of a keyword into data frame
        df[keyword] = sentiment_scores

        # Sort the companies based on sentiment score
        sorted_entities = sorted(entities, key=lambda x: sentiment_scores[entities.index(x)],reverse=True)

        # Create temporary data frame only with required columns and this will be used in the vbar glyph
        temp_df = df[["entity", keyword]]
        temp_df['total'] = total
        temp_df['positive'] = total_pos
        temp_df['negative'] = total_neg

        # Add sorted entities column to data frame
        temp_df['sorted_entities'] = sorted_entities

        # Rename the keyword column to sentiment_score
        temp_df.rename(columns={keyword: 'sentiment_score'}, inplace=True)
        source = ColumnDataSource(temp_df)

        # Initialize the plot
        p = figure(
          x_range=sorted_entities,
          plot_width = 900
          )

        # Style the tools
        p.tools=[SaveTool(),ResetTool()]

        # Remove the Bokeh default logo
        p.toolbar.logo=None

        # Add Hovering
        hover = HoverTool()
        hover.tooltips = """
            <div>
                <div>
                    <span style="float: center;font-size: 15px; font-weight: bold; color: #696;"><center>@entity</center></span>
                </div>
                <div>
                    <span style="font-size: 15px; font-weight: bold;">Score:</span>
                    <span style="font-size: 13px; color: #966;">@sentiment_score{0.000}</span>
                </div>

                <div>
                    <span style="font-size: 15px; font-weight: bold;">Total Documents:</span>
                    <span style="font-size: 13px; color: #966;">@total</span>
                </div>

                <div>
                    <span style="font-size: 15px; font-weight: bold;">Positive Documents:</span>
                    <span style="font-size: 13px; color: #966;">@positive</span>
                </div>

                <div>
                    <span style="font-size: 15px; font-weight: bold;">Negative Documents:</span>
                    <span style="font-size: 13px; color: #966;">@negative</span>
                </div>
            </div>
        """
        p.add_tools(hover)

        # Style the title
        p.title.text=keyword.title() 
        p.title.text_color="green"
        p.title.text_font="Decorative"
        p.title.text_font_size="30px"
        p.title.align="center"

        # Style the Axis
        p.yaxis.axis_label="Negative Sentiment                Positive Sentiment"
        p.axis.major_label_text_font="Times"
        p.axis.major_label_text_font_size="20px"
        p.axis.axis_label_text_font="Verdana"
        p.axis.axis_label_text_font_size="20px"

        # Style the Grid
        p.xgrid.grid_line_color = None

        # Axis Geometry
        p.y_range=Range1d(start=-1,end=1)
        p.yaxis[0].ticker.desired_num_ticks=10

       # Call the Bokeh's vbar glyph
        p.vbar(
            x='entity',
            top='sentiment_score',
            width=width,
            legend='entity',

            fill_color=factor_cmap(
                'entity',
                palette=Magma10,
                factors=sorted_entities,
                nan_color='white'
            ),
            source = source
        )

        # Add NO DATA label where there is no data
        df_nodata = temp_df.loc[temp_df['total'] == 0]
        if not df_nodata.empty:
            pd.options.mode.chained_assignment = None
            df_nodata.loc[:, 'text'] = 'NO DATA'
            source_nodata = ColumnDataSource(df_nodata)
            labels = LabelSet(x='entity', y=0, text='text', text_align='center', text_color='red', source=source_nodata)
            p.add_layout(labels)

        # Legend
        p.legend.orientation = "horizontal"
        p.legend.location = "top_center"
        p.hover.mode = "vline"

        # Save the Bokeh components
        script_t, div_t = components(p)
        images.append({'script': script_t, 'div': div_t})

    #save sentiment logs
    #yogi#log_df = pd.DataFrame(log_df)
    #yogi#log_df.to_csv("/root/data/results_log.csv", sep=",", index=False)

    # Generate the stacked bar graph if more than one keyword is chosen
    if length_keywords > 1:
        columns = list(df)
        data = df.to_dict('list')

        f = figure(x_range=entities, title="Overall Sentiment Score per Company", plot_width = 1050,
            tools="save, reset")
        hover = HoverTool()
        hover.tooltips = """
            <div>
                <span style="font-size: 15px; font-weight: bold;">$name:</span>
                <span style="font-size: 13px; color: #966;">@$name{0.000}</span>
            </div>
        """
        f.add_tools(hover)
        # Remove the Bokeh default logo
        f.toolbar.logo=None

        # Style the title
        f.title.text="Overall Sentiment Score per Company"
        f.title.text_color="green"
        f.title.text_font="Decorative"
        f.title.text_font_size="30px"
        f.title.align="center"

        # Style the Axis
        f.yaxis.axis_label="Sentiment Score"
        f.axis.major_label_text_font="Times"
        f.axis.major_label_text_font_size="20px"
        f.axis.axis_label_text_font="Verdana"
        f.axis.axis_label_text_font_size="20px"

        # Axis Geometry
        f.yaxis[0].ticker.desired_num_ticks=10

       # Call the Bokeh's vbar_stack glyph
        f.vbar_stack(keywords, x='entity', width=width, color=colors, source=data,
                        legend=[value(x) for x in keywords])

        f.xgrid.grid_line_color = None
        f.legend.orientation = "horizontal"
        f.legend.location = "top_center"

        # Save the Bokeh components
        script_stack, div_stack = components(f)
        return render(request, 'results.html', { 'images' : images, 'keywords': keywords, 'script_stack': script_stack, 'div_stack': div_stack})

    return render(request, 'results.html', { 'images' : images, 'keywords': keywords})
