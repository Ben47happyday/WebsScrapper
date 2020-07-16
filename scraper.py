import requests 
from pyodbc import connect as cnn
import urllib.request 
import time 
from bs4 import BeautifulSoup
import json
import re , wmi
import numpy as np


#load configuration file 

with open("config.json","r") as j:
    config = json.load(j)


_min = int(config[0]["min price"].replace(",","")) 
_max = int(config[0]["max price"].replace(",","")) 
_inc = int(config[0]["step amount"].replace(",","")) 

print("Start")
_page = 1
_suburb = config[0]["suburb"]

_resultContent = []

# connect MS SQL database
_conn = cnn ('Driver={SQL Server};'
                            f'Server=walkie-talkie\manteauDev;'
                            'Database=Properties;'
                            'Trusted_Connection=yes;')


for i in range (_min,_max,_inc):

    _start_price = i
    _end_price = i + _inc
    _page_end = False 
    _page = 1

    while _page_end == False:

        url = f"https://www.domain.com.au/sale/{_suburb}-nsw-2076/?price={_start_price}-{_end_price}&enablemobilemap=1&page={_page}"

        
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, headers = headers, proxies={'http':'50.207.31.221:80'})

        #break while loop if response return 400 
        if response.status_code in (400, 403):
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
            baths = propertyjson["listingSummary"]["baths"]
            propertyid = propertyjson["id"]
            suburb = propertyjson.get("suburb","")
            postcode = propertyjson.get("postcode","")
            profileCreatedOn = propertyjson.get("createdOn","")
            profileModifiedOn = propertyjson.get("modifiedOn","")
            
            try:
                parking = propertyjson["listingSummary"]["parking"]
            except:
                parking = ""
            try:
                Nextinspection = propertyjson["inspection"]["inspectionTimes"][0]
            except:
                Nextinspection = ""

            _resultContent.append({"Property ID": propertyid ,"URL":propertyurl,"address":add, "price":price, "beds":beds, "baths":baths, "parking":parking, "type":propertyType, "Next Inspection":Nextinspection, "suburb":suburb, "postcode" : postcode, "profileCreatedOn": profileCreatedOn, "profileModifiedOn":profileModifiedOn})  

            # result = "\n URL: {} \n Property address: {} \n guid price: {} \n bedroom: {} \n type: {} ".format(propertyurl,add,price,beds,propertyType) 

            # _resultContent += result
            _page += 1 

with open(f"result.json","w") as j:
        json.dump(_resultContent,j)


# execute sql procedure to load data into database

#bulk insert data into staging

_conn.execute("exec [stage].[Load_property_detail]")
_conn.commit()
print ("executed [stage].[Load_property_detail]") 
# merge into target table 
_conn.execute("exec [dbo].[Load_property_detail]")
_conn.commit()
print ("executed [dbo].[Load_property_detail] to merge into target table") 

print ("Completed !")