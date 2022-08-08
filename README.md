# ScrapeNewsWebsitesUsingGoogleCustomSearch

Python script for scraping news stories from news websites which contain keywords of interest. 

## Instructions

After Cloning this repo to your local machine, run the following to initialize the Conda environment

'''
conda create -n scrape-google pandas numpy matplotlib scikit-learn jupyter notebook
conda activate scrape-google
python3 -m ipykernel install --user --name=scrape-google
'''

Then install the additional software dependencies using:

'''
pip install -r requirements.txt 
'''

Before you use this code, you will need to create a GoogleAPI account and set up Google Custom Search. I found this video helpful: https://www.youtube.com/watch?v=IBhdLRheKyM

For each of the websites you are interested in, certain information must be stored in the file "lookupWebsite.csv". First, the name of the website which is the text you will refer to in Python script. Second, you must include the GoogleCustomSearch code that links your code to the GoogleCustomSearch API (see the above video).

Though you are able to scrape a small number of articles per day for free, you will need to pay if you want to scale this up. See here for details: https://developers.google.com/custom-search/docs/overview 

Run ScrapeNewsWebsite.py to do the following:

1. save list of url's for each news website in your list. Each url will be associated with a keyword search term and url's can appear multiple times if it links to a news story that contains multiple keywords.

2. scrape the article text and other metadata from the url's. The headings are: 'url', 'googleDate', 'title', 'text', 'authors', 'keywords', 'date', 'image' and 'request'


## Things to do

* When URL's are scraped, save description from Google search
* Use constant information bars (rather than constant time bars) when time slicing Google Searches (Probably using Google trends data as a proxy for interest in a given keyword)
* fold keywords contained in the url dataframe into the corresponding main dataframe (must allow for the possibility of multiple keywords per news story)
