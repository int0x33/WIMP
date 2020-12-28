from pocket import Pocket, PocketException
import json
import os

// Sign up to pocket API then get tokens here: https://reader.fxneumann.de/plugins/oneclickpocket/auth.php
p = Pocket(
consumer_key='',
access_token=''
)

# Fetch a list of articles
try:
    lis = p.retrieve(offset=0, count=1000)
    for i in lis['list']:
        if "github.com" in lis['list'][i]['given_url']:
            print(lis['list'][i]['given_url'])
            os.system("git clone {}".format(lis['list'][i]['given_url']))
            p.delete(i)
except PocketException as e:
    print(e.message)
