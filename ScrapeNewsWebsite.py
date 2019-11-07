from googleapiclient.discovery import build
import numpy as np
import pandas as pd
from dateutil.parser import parse
from newspaper import Article
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
import time
import datetime
import calendar
import os
import shutil
import csv


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)


def connectToGoogle():
    api_name = 'customsearch'
    api_version = 'v1'
    api_key = 'insertapikey' ## insert your own GoolgeCustomSearchAPI
    service = build(api_name, api_version,developerKey=api_key).cse()
    return service

def isDate(string):
    try:
        dt=parse(string, fuzzy=True)
    except ValueError:
        #print('no date in string')
        dt = np.nan
        
    return dt



def updateUrlTable(web,df):
    Z = set(zip(list(df['url']),list(df['keyword'])))
    columns = ['url_'+web,'keyword'] #'id',
    quesString = ','.join(['?']*len(columns))
    colString = ','.join(columns)

    websourceSQL = "INSERT INTO " + web + '_url' + ' (' + colString + ') VALUES (' + quesString + ")"
    cur.executemany(websourceSQL, Z)
    


def searchGoogleGrabURL(web, keyword, numOfSearchPages = 10,startDate=datetime.date(2014,1,1)):
    
    websiteCode = lookup.loc[web,'code']
    
    endDate=add_months(startDate, 1)

    today = datetime.date.today()
    #num_months = 68

    totalResults=0
    while startDate < today:
        
        #convert newDates to string
        startString = startDate.strftime("%Y-%m-%d")
        endString = endDate.strftime("%Y-%m-%d")

        dateQuery = ' after:' + startString + ' before:' + endString

        start=1
        for _ in range(numOfSearchPages):
            
            res = service.list(q=keyword+dateQuery, cx=websiteCode, start=start).execute()
            time.sleep(1) #delay next request by 1 second

            print('number_urls:',totalResults,' date:',startString) #percetage complete

            try: 
                N = len(res['items']) #3

                urls=[res['items'][i]['link'] for i in range(N)]#['nosh','nosh2','nosh3'] #
                dates=[isDate(res['items'][i]['snippet']) for i in range(N)] #[1,2,3]#
                keywords = [keyword]*N

                df=pd.DataFrame([urls,keywords,dates]).T
                df.to_csv('url/'+web, mode='a', header=False,index=False)

                totalResults+=N
                start+=N

            except (KeyError,ValueError,OverflowError):
                break

        #increment dates
        startDate = add_months(startDate, 1)
        endDate = add_months(endDate, 1)
        
    return

def numberOfResults(web, keyword, numOfSearchPages = 10):
    
    websiteCode = lookup.loc[web,'code']

    URLS = []
    KEYWORDS = []
    DATES = []


    start=1
    for _ in range(numOfSearchPages):

        res = service.list(q=keyword, cx=websiteCode, start=start).execute()
        time.sleep(1) #delay next request by 1 second
        print('number_urls:',len(URLS)) #percetage complete

        try: 
            N = len(res['items']) #3

            urls=[res['items'][i]['link'] for i in range(N)]#['nosh','nosh2','nosh3'] #
            dates=[isDate(res['items'][i]['snippet']) for i in range(N)] #[1,2,3]#
            keywords = [keyword]*N

            URLS.extend(urls)
            DATES.extend(dates)
            KEYWORDS.extend(keywords)

            start+=N

        except KeyError:
            break

    df=pd.DataFrame([URLS,KEYWORDS,DATES]).T

    return df

def countURL(web):
    Z=pd.read_csv('url/'+web,header=None)
    Z.drop_duplicates(subset =0,keep='first',inplace=True)
    print('number of unique urls:',Z.shape[0])
    
    return

def backupURL(web):
    src = 'url/'+web
    dest = 'backupURL/' + web
    
    shutil.copyfile(src, dest)
    
def addCsvTablesIfNotExist(web):
        
    L=os.listdir('data/')
    if web not in L: 
        df = pd.DataFrame(columns=['url','googleDate','title','text','authors','keywords','date','image','request'])
        df.to_csv('data/'+web)
        print('new data table:', web)
    return

def getURLsNotInAlreadyInTable(web):

    df=pd.read_csv('url/'+web,header=None)
    df.drop_duplicates(subset =0,keep='first',inplace=True)
    newURL = df.iloc[:,0]

    dfData=pd.read_csv('data/'+web,index_col=0)
    currentURL = dfData.loc[:,'url']


    urlToAdd = np.setdiff1d(newURL, currentURL)

    dfUrlDate = df.loc[:,[0,2]]

    
    return urlToAdd,dfUrlDate


def scrapeNews(url,dfUrlDate):
    try:
        article_name = Article(url)

        article_name.download()
        article_name.parse()

        text = article_name.text
        #text = leaveOnlyContentWords(text) 

        #print(w)

        title = article_name.title
        #title = leaveOnlyContentWords(title)

        authors = article_name.authors
        authors = ', '.join(authors)

        keys = article_name.keywords
        keys = ', '.join(keys)

        date = article_name.publish_date
        if date != None: date = date.strftime("%m/%d/%Y")

        image = article_name.top_image

        dt = datetime.datetime.utcnow().date().strftime("%m/%d/%Y")

        googleDate = dfUrlDate[dfUrlDate.iloc[:,0] == url].iloc[:,1].values[0]



        Z = (url,googleDate,title,text,authors,keys,date,image,dt)


        return Z

    except BaseException as e:
        pass
    
def addContentToSQL(web,content):
    columns=['url','googleDate','title','text','authors','keywords','date','image','request']
    D=pd.Series(content,index=columns)
    D=pd.DataFrame(D).T
    D.to_csv('data/'+web, mode='a', quoting=csv.QUOTE_MINIMAL,header=False)#, header=False,index=False)

    
    


# news websites to scrape (make sure GoogleCustomSearchCode is saved in lookupWebsite.csv)
websiteList = ['AP','BBC','Reuters','DW']

# keywords (topics) of interest. Search each of the websites for each of these keywords 
keywordList = ['"vaccine"','"dakota access pipeline"','"ebola"', '"GMO"', '"genetically modified organism"', 
               '"vacc"', '"vax"', '"zika"','"frack"', '"pasteuriz"', '"paris climate"', '"clean coal"'] 
    
    
    

    
    
# Use Google Custom Search to save list of website url's for news stories containing certain keywords

lookup=pd.read_csv('lookupWebsite.csv',index_col=0) # lookup table for news websites

numOfSearchPages = 10 #maximum number of search pages is 10
    
### get URL's and GoogleDates for each website-keyword
service = connectToGoogle()
    
for web in websiteList:
    for keyword in keywordList:
        print(web,keyword)
        
        #search over all dates and save results
        df=numberOfResults(web, keyword, numOfSearchPages = 10)
        df.to_csv('url/'+web, mode='a', header=False,index=False)
        
        if df.shape[0] < 85:
            print('only ' + str(df.shape[0]) + ' stories found, so just save them')
        else:
            print('over ' + str(df.shape[0]) + ' stories found, so perform monthy searches')
            searchGoogleGrabURL(web, keyword, numOfSearchPages = 10)#,startDate=datetime.date(2019,6,1))
            
        countURL(web)
        backupURL(web)
        
        
        
        
#create empty table for a new news website
for web in websiteList: addCsvTablesIfNotExist(web)
    
#scrape information from the urls saved in the previous step
for web in websiteList:

    urlToAdd,dfUrlDate = getURLsNotInAlreadyInTable(web)

    print('number of new urls for ' + web + ':', urlToAdd.shape[0])

    for url in urlToAdd:
        content = scrapeNews(url,dfUrlDate)
        if content != None: #if url has been scraped succesfully, then add to database
            addContentToSQL(web,content)

    numOfArticles = pd.read_csv('data/'+web,index_col=0).shape[0]
    print('number of recovered articles for ' + web + ':', numOfArticles)
