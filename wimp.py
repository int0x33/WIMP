from pocket import Pocket, PocketException
import json
import os
import requests

import sys
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import urllib.parse
import base64

from datetime import date
today = date.today()
d3 = today.strftime("%m/%d/%y")

# Your own API!
url = ""
headers = { 'Content-Type': 'application/x-www-form-urlencoded' }

p = Pocket(
consumer_key='',
access_token=''
)

os.system("mkdir -p ~/youtube && mkdir -p ~/opt && mkdir -p ~/tweets && mkdir -p ~/html && mkdir -p ~/pdf")

# TO DO: Fix Medium 404s

# Fetch a list of articles
try:
    lis = p.retrieve(offset=0, count=10000)
    for i in lis['list']:
        print(lis['list'][i]['given_url'])
        if "github.com" in lis['list'][i]['given_url']:
            os.system("cd ~/opt && git clone {} &".format(lis['list'][i]['given_url']))
        if ".pdf" in lis['list'][i]['given_url']:
            os.system("wget {} -P ~/pdf &".format(lis['list'][i]['given_url']))
        if "/status/" in lis['list'][i]['given_url']:
            os.system("curl https://publish.twitter.com/oembed?url={} > ~/tweets/{}.json &".format(lis['list'][i]['given_url'], i))
        if "www.youtube.com" in lis['list'][i]['given_url']:
            os.system("cd ~/youtube && echo '{}' >> video_list.txt &".format(lis['list'][i]['given_url']))
        else:
            r = requests.get(lis['list'][i]['given_url'])
            doc = r.text
            soup = BeautifulSoup(doc, 'lxml')
            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            # get text
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            print(text)

            n_gram_range = (3, 3)
            stop_words = "english"

            # Extract candidate words/phrases
            count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([text[:512]])
            candidates = count.get_feature_names()

            model = SentenceTransformer('distilbert-base-nli-mean-tokens')
            doc_embedding = model.encode([text[:512]])
            candidate_embeddings = model.encode(candidates)

            top_n = 5
            distances = cosine_similarity(doc_embedding, candidate_embeddings)
            keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]
            print(keywords)

            encodedBytes = base64.b64encode(doc.encode("utf-8"))
            encodedHtml = str(encodedBytes, "utf-8")

            encodedBytes = base64.b64encode(text.encode("utf-8"))
            encodedText = str(encodedBytes, "utf-8")

            payload = 'title='+soup.title.text+'&html='+encodedHtml+'&keywords='+urllib.parse.quote_plus(str(keywords))+'&text='+encodedText+'&added='+d3
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text.encode('utf8'))

        print(p.delete(i))
except PocketException as e:
    print(e.message)
p.commit()
                         
