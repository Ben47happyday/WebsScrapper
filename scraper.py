import requests 
import urllib.request 
import time 
from bs4 import BeautifulSoup
import json
import re 


num = 1

url = 'https://www.domain.com.au/sale/wahroonga-nsw-2076/?excludeunderoffer=1'
response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")

tags = soup.findAll("link", {"itemprop":"url"})


for eachLink in tags: 
    propertyurl = eachLink['href']
    print ("Property URL: "+ propertyurl)
    propertyreponse = requests.get(propertyurl)
    propertysoup = BeautifulSoup(propertyreponse.text,'html.parser')
    propertytags = propertysoup.findAll('script', text = re.compile('window\[\'__domain_group/APP_PROPS\'\]') )
    tag_string = str(propertytags[0].contents[0]) 

    json_string =tag_string.replace("window[\'__domain_group/APP_PROPS\'] =","").replace("; window['__domain_group/APP_PAGE'] = 'listing-details'",'')

    propertyjson = json.loads(json_string)
    name = propertyjson["address"].replace ('/','_').replace('-','_')

    print("Property address: {} guid price: {} bedroom: {} , )

    # with open(f"properties\{name}.json","w") as j:
    #     json.dump(propertyjson,j)
