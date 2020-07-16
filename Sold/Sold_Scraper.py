import requests 
from pyodbc import connect as cnn
import urllib.request 
import time 
from bs4 import BeautifulSoup
import json, re , wmi,requests
from datetime import datetime


print("Start Scrap Domain for Sold Properties")

# connect MS SQL database

def decode_soup (soup, price):

    # Slice property ID
    try:
        listID = soup.li['data-testid']
    except:
        return 0 

    SoldPropertyID = int(listID[listID.find('-')+1:])
    
  
    SoldComment = soup.find_all("span", class_="css-1nj9ymt")[0].contents[0]
    # Slice sold comment to capture sold date
    spacecount = 0 
    spaceindex = 0
    revStr = SoldComment[::-1]
    for index , l in enumerate(list(revStr)): 
        if l == " ":
            spacecount +=1
            if spacecount == 3:   
                spaceindex = index


    getdate = SoldComment[::-1][:spaceindex][::-1]
    try:
        SoldDate = datetime.strptime(getdate, '%d %b %Y').strftime('%Y-%m-%d')
    except: 
        try:
            SoldDate = datetime.strptime(getdate, '%d %B %Y').strftime('%Y-%m-%d')
        except:
            SoldDate = '1900-01-01'
    
    
    #if price with held , turn priceWithHeld flag on
    _SoldPrice = soup.find_all('p',attrs = {"data-testid":"listing-card-price"})[0].next_element.strip().replace('$','').replace(',','') 
    if _SoldPrice == 'Price Withheld': 
        PriceWithHeld = 1 
        SoldPrice = price
    else:
        SoldPrice = int(_SoldPrice)
        PriceWithHeld = 0 

    
    SoldURL = soup.a["href"].strip()
    SoldPropertyName = soup.meta["content"].strip()
    SoldPropertyType = soup.find_all("span", class_="css-693528")[0].next.strip()
    try: 
        SoldBeds = soup.find_all("span", attrs = {"data-testid":"property-features-text-container"})[0].next.strip()
    except IndexError: 
        SoldBeds = 0 
    try:
        SoldBath = soup.find_all("span", attrs = {"data-testid":"property-features-text-container"})[1].next.strip()
    except IndexError: 
        SoldBath = 0 
    try:
        SoldPark = soup.find_all("span", attrs = {"data-testid":"property-features-text-container"})[2].next.strip()
    except IndexError: 
        SoldPark = 0 

    if SoldPropertyType.lower().find("land") != -1:
        SoldBeds = 0 
        SoldBath = 0 
        SoldPark = 0 
    
    if str(SoldBath).isnumeric() == False:
        SoldBath = 0 
    if str(SoldBeds).isnumeric() == False:
        SoldBeds = 0
    if str(SoldPark).isnumeric() == False:
        SoldPark = 0 

    try:
        SoldLandSize = soup.find_all("span", attrs = {"data-testid":"property-features-text-container"})[3].next.strip()
    except IndexError: 
        SoldLandSize = 'Unkonw'

    try:
        SoldStreetAddress = soup.find_all("span", attrs = {"data-testid":"address-line1"})[0].next.strip()
    except IndexError:
        SoldStreetAddress = 'Unknow'
    #iterate address 2 for re-sort

    addressDetails = soup.find_all("span", attrs = {"data-testid":"address-line2"})[0].contents
    addressAdd = [i.next for i in addressDetails if i != " "]
        
    SoldSuburb = addressAdd[0]
    SoldState = addressAdd[1]
    SoldPostcode = addressAdd[2]

    dic = { 
            "Property ID":SoldPropertyID,
            "Sold Comment": SoldComment, 
            "Sold Price":SoldPrice, 
            "Property Name" : SoldPropertyName, 
            "Property Type" : SoldPropertyType,
            "Beds":SoldBeds,
            "Bath":SoldBath,
            "Parking":SoldPark,
            "Land Size":SoldLandSize,
            "Sold Date":SoldDate,
            "URL" :SoldURL,
            "Street": SoldStreetAddress,
            "Suburb": SoldSuburb,
            "State" : SoldState,
            "Post Code" : SoldPostcode,
            "Price With Held" : PriceWithHeld
            } 
            

    return dic



# comment end

#Open sample static webpage html
# with open('webpage.html','r') as f:
#     test_response = f.read()

def scraper (suburb, state, postcode):

    _page = 1
    _priceRange1 = 100000
    _priceRange2 = 30000000
    _inc = 100000
    # SQL Server Connection config
    _conn = cnn ('Driver={SQL Server};'
                            f'Server=walkie-talkie\manteauDev;'
                            'Database=Properties;'
                            'Trusted_Connection=yes;')

    for _price in range(_priceRange1, _priceRange2, _inc): 

        while 1:

            propertyList_List = []
            
            if _page == 1: 
                _pageStr = ""
                _page = ""
            else:
                _pageStr = "&page="

            # request webpage source code
            headers = {'User-Agent': 'Mozilla/5.0'}
            _price2 = _price + _inc

            #Sample URL 
            #https://www.domain.com.au/sold-listings/pymble-nsw-2073/?price=3500000-9000000&ssubs=0
            url = f"https://www.domain.com.au/sold-listings/{suburb}-{state}-{postcode}/?price={_price}-{_price2}&ssubs=0{_pageStr}{_page}"
            # demo URL
            # url = "https://www.domain.com.au/sold-listings/Wahroonga-NSW-2076/?price=700000-800000&ssubs=0&page=10"

            if _page == "":
                _page = 1
            
            _page = _page + 1

            response = requests.get(url, headers = headers, proxies={'http':'50.207.31.221:80'})

            # break the loop the response with status code as error
            if response.status_code in (400, 403):
                print("response status {}".format(response.status_code)) 
                break

            print ("request response from {}".format(url)) 


            soup = BeautifulSoup(response.text,"html.parser")

            if soup.h3.next == 'No exact matches':
                _page = 1 
                print ('    No Eact Matches')
                break

            propertyList = soup.find_all("li",class_="css-1b4kfhp")

            # cast tag object to soup object
            propertyList_soups = [BeautifulSoup(str(i),"html.parser") for i in propertyList] 


            for i , s in enumerate(propertyList_soups):
                
                if decode_soup(s,0):
                    # pass middile price for price range to instead price which with held
                    midPrice =  (_price + _price2) / 2  
                    property_dic = decode_soup(s, midPrice)
                    propertyList_List.append(property_dic)
                    propertyID = int(property_dic['Property ID']) 
                    print ("  List Page [{}] Fetch Soup [{}] Property Name [{}]".format(_page-1, i,property_dic["Property Name"])) 
            
            print ('    Encode into Json File.....')
            with open(f'Sold_Properties.json','w') as f:
                json.dump(propertyList_List,f)
            
            print ('    Json File Updated !')

            _conn.execute(" exec [stage].[Load_Sold_Properties]")
            _conn.commit()
            print ("    executed [stage].[Load_Sold_Properties]") 
            # merge into target table 
            _conn.execute("exec [dbo].[Merge_Sold_Property_to_Target]")
            _conn.commit()
            print ("    executed [dbo].[Merge_Sold_Property_to_Target] to merge into target table") 


print('Web Suck Completed ')



