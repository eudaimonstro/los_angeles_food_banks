# -*- coding: utf-8 -*-

"""Main module."""

import os
import sys
import subprocess
import requests
import pprint
import time
import json
import re
from bs4 import BeautifulSoup

print = pprint.pprint

GOOGLE_API_KEY = 'AIzaSyBG6zA1Oo8rBoM84gm4ow9sJvAz7Fp4mss'

BANK_IDS = set()

googleRequestCounter = 0
laBankCounter = 0
suntopiaBankCounter = 0
totalBankCounter = 0

def parseLAZipPdf():
    print("Entering parseLAZipPdf")

    bashOne = "pdftotext -eol unix data/zip_codes.pdf -"
    bashTwo = "egrep ^[0-9]{5}"
    p1 = subprocess.Popen(bashOne.split(), stdout=subprocess.PIPE);
    p2 = subprocess.Popen(bashTwo.split(), stdin=p1.stdout, stdout=subprocess.PIPE);
    with open('data/zip_codes.txt', 'w') as f:
        f.write(p2.communicate()[0].decode("utf-8"))

    print("Leaving parseLAZipPdf")
    
def getZipList():
    print("Entering getZipList")

    with open('data/zip_codes.txt') as f:
        zips = f.readlines()
    
    print("Leaving getZipList")
    
    return [x.strip() for x in zips]

def getZipLatLng():
    print("Entering getZipLatLng")
    global laBankCounter
    global suntopiaBankCounter
    global totalBankCounter
    global googleRequestCounter

    if os.path.exists('data/locations.json') and time.time() - os.path.getmtime('data/locations.json') < 86400:
        with open('data/locations.json') as f:
            return json.load(f)

    results = []
    for code in getZipList():
        googleRequestCounter += 1
        response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={str(code)}&key={GOOGLE_API_KEY}")
        results.append(response.json())

    with open('data/locations.json', 'w') as f:
        json.dump(results, f)

    print("Leaving getZipLatLng")

    return results

def getBanksLAFood():
    print("Entering getBanksLAFood")
    global laBankCounter
    global suntopiaBankCounter
    global totalBankCounter
    global googleRequestCounter
    global BANK_IDS

    # if os.path.exists('banksLAFood.json') and time.time() - os.path.getmtime('banksLAFood.json') < 86400:
    #   with open('banksLAFood.json') as f:
    #     return json.load(f)

    bankResults = {"results": []}
    bankLAFoodIds = set()
    codes = getZipLatLng()
    for code in codes:
        
        lat = code['results'][0]['geometry']['location']['lat']
        lng = code['results'][0]['geometry']['location']['lng']
        response = requests.get(f"https://www.lafoodbank.org/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&max_results=25&search_radius=15")
        for bank in response.json():
            if bank['id'] in bankLAFoodIds:
                continue

            bankLAFoodIds.add(bank['id'])

            address = bank['address'] + " " + bank['city'] + " " + bank['state']
            
            googleRequestCounter += 1
            response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}")
            responseJson = response.json()

            if(len(responseJson['results'])) > 1:
                print(f"Location with multiple results: {bank['store']} {address}")
            if(len(responseJson['results'])) < 1:
                print(f"Location with no results: {bank['store']} {address}")
                continue

            placeId = responseJson['results'][0]['place_id']

            if placeId not in BANK_IDS:
                laBankCounter += 1
                responseJson["results"][0]['name'] = bank['store']
                responseJson["results"][0]['hours'] = bank['fax']
                bankResults['results'].append(responseJson["results"][0])
                BANK_IDS.add(placeId)

                printUpdate(bank['store'], address, bank['fax'])

    with open('data/banksLAFood.json', 'w') as f:
        json.dump(bankResults, f)

    return bankResults

    print("Leaving getBanksLAFood")

def getBanksSuntopia():
    print("Entering getBanksSuntopia")
    global laBankCounter
    global suntopiaBankCounter
    global totalBankCounter
    global googleRequestCounter
    global BANK_IDS

    # if os.path.exists('banksSuntopia.json') and time.time() - os.path.getmtime('banksSuntopia.json') < 86400:
    #   with open('banksSuntopia.json') as f:
    #     return json.load(f)
    bankResults = {"results": []}
    for page in range(1, 20):
        response = requests.get(f"http://www.suntopia.org/los_angeles/ca/food_pantries.php?page={page}")
        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.article.find_all('div')
        for i in range(len(divs) - 2):
            rows = divs[i].find_all('tr')
            title = rows[0].td.contents[0].string.strip()
            if page == 1 and i == 0:
                continue

            addressNumber = rows[1].td.string.strip() + " "
            r = re.compile(', CA')
            h = re.compile('Hours:')
            addressDetails = ""
            hours = ""

            aTags = divs[i].find_all(string=re.compile(', CA'))
            bTags = divs[i].find_all("b",string=re.compile('^Hours:'))
            if len(aTags) == 1:
                addressDetails = aTags[0].string
            if len(bTags) == 1:
                if bTags[0].next_sibling.string is not None:
                    hours = bTags[0].next_sibling.string
                else:
                    hours = bTags[0].next_sibling.next_sibling.string
            
            address = title + " " + addressNumber + addressDetails
            
            googleRequestCounter += 1
            response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}")
            responseJson = response.json()
            
            if(len(responseJson['results'])) > 1:
                print(f"Location with multiple results: {title}")

            if(len(responseJson['results'])) < 1:
                print(f"Location with no results: {title}")
                continue

            placeId = responseJson['results'][0]['place_id']
            if placeId not in BANK_IDS:
                suntopiaBankCounter +=1
                responseJson['results'][0]['name'] = title
                responseJson['results'][0]['hours'] = hours
                bankResults['results'].append(responseJson["results"][0])
                BANK_IDS.add(placeId)

                printUpdate(title, addressNumber + addressDetails, hours)

    with open('data/banksSuntopia.json', 'w') as f:
        json.dump(bankResults, f)

    return bankResults

    print("Leaving getBanksSuntopia")

def createBankLocations():
    print("Entering createBankLocations")

    banksLAFood = getBanksLAFood()
    suntopiaBanks = getBanksSuntopia()

    # with open('data/banksLAFood.json') as f:
    #   banksLAFood =json.load(f)
    # with open('data/banksSuntopia.json') as f:
    #   suntopiaBanks =json.load(f)

    banks = banksLAFood['results'] + suntopiaBanks['results']
    
    with open('data/banks.json', 'w') as f:
        json.dump(banks, f)

    sendBankJSON()

    print("Leaving createBankLocations")

def sendBankJSON():
    bash = "scp data/banks.json droplet:/var/www/html"
    subprocess.run(bash.split())

def printUpdate(name, address, hours):
    global laBankCounter
    global suntopiaBankCounter
    global totalBankCounter
    global googleRequestCounter

    totalBankCounter = laBankCounter + suntopiaBankCounter

    print("Total: " + str(totalBankCounter))
    print("LA Bank: " + str(laBankCounter))
    print("Suntopia: " + str(suntopiaBankCounter))
    print("Google Requests: " + str(googleRequestCounter))

createBankLocations()