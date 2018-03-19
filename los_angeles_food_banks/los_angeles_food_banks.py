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



BANK_IDS = set()



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
