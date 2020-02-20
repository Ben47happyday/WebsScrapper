import requests 
import urllib.request 
import time 
from bs4 import BeautifulSoup
import json
import re 


_min = 1000000
_max = 1200000
_inc = 100000

_page = 1
_suburb = 'wahroonga'

_resultContent = []

for i in range (_min,_max,_inc):

    _start_price = i - _inc
    _end_price = i 
    _page_end = False 
    _page = 1

    while _page_end == False:

        url = f"https://www.domain.com.au/sale/{_suburb}-nsw-2076/?price={_start_price}-{_end_price}&enablemobilemap=1&page={_page}"

     
        
        response = requests.get(url)

        if response.status_code == 400:
            _page_end = True
            print("response status {}".format(response.status_code)) 
            break



        soup = BeautifulSoup(response.text,"html.parser")

        tags = soup.findAll("link", {"itemprop":"url"})
        if tags == []:
            break
        
        print ("\nURL: {}\npage number: {}\nprice range {} - {}".format(url,_page,_start_price,_end_price) )

        for eachLink in tags: 
            propertyurl = eachLink['href']

            print ("   Property URL: "+ propertyurl)

            propertyreponse = requests.get(propertyurl)
            propertysoup = BeautifulSoup(propertyreponse.text,'html.parser')
            propertytags = propertysoup.findAll('script', text = re.compile('window\[\'__domain_group/APP_PROPS\'\]') )
            tag_string = str(propertytags[0].contents[0]) 

            json_string =tag_string.replace("window[\'__domain_group/APP_PROPS\'] =","").replace("; window['__domain_group/APP_PAGE'] = 'listing-details'",'')

            propertyjson = json.loads(json_string)
            add = propertyjson["address"].replace ('/','_').replace('-','_')
            p_id = propertyjson["id"]
            beds = propertyjson["beds"]
            propertyType = propertyjson["propertyType"]
            #price = propertyjson["listingsMap"][f"{p_id}"]["listingModel"]["price"]
            price = (_end_price + _start_price) / 2 

            
            _resultContent.append({"URL":propertyurl,"address":add, "price":price, "beds":beds, "type":propertyType})  

            # result = "\n URL: {} \n Property address: {} \n guid price: {} \n bedroom: {} \n type: {} ".format(propertyurl,add,price,beds,propertyType) 

            # _resultContent += result
            
            _page += 1 

with open(f"result.json","w") as j:
        json.dump(_resultContent,j)
