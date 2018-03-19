import requests
import re
import pprint
import os
import json
from bs4 import BeautifulSoup
from bank import Bank

from names import GOOGLE_API_KEY
from names import dataFolder


class Suntopia:
    def __init__(self, testing=False, nofetch=False, idList=set()):
        self.__isTesting = testing
        self.__isNoFetch = nofetch
        self.banks = set()
        self.bankIds = idList
        self.googleMapsUrl = "https://maps.googleapis.com/maps/api/geocode/json"
        self.suntopiaPageUrl = "http://www.suntopia.org/los_angeles/ca/food_pantries.php"
        self.startPage = 1
        self.endPage = 19
        if self.__isTesting:
            self.startPage = 2
            self.endPage = 3

    def getBankGoogleInfo(self, bank):
        if self.__isNoFetch:
            with open(os.path.join(dataFolder, 'suntopiaGoogle.txt'), 'r') as f:
                storedResponses = json.load(f)
                return storedResponses[bank.name]
        urlParams = f"?address={bank.name + bank.address}&key={GOOGLE_API_KEY}"
        url = self.googleMapsUrl + urlParams

        response = requests.get(url)

        infoJson = response.json()

        if(len(infoJson['results'])) > 1:
            bankId = None
            coords = (None, None)
        elif(len(infoJson['results'])) < 1:
            bankId = None
            coords = (None, None)
        else:
            bankId = infoJson['results'][0]['place_id']
            coords = (infoJson['results'][0]['geometry']['location']['lat'], infoJson['results'][0]['geometry']['location']['lng'])
        return bankId, coords, response

    def parseBankName(self, bankDiv):
        tdList = bankDiv.find_all('td')
        if len(tdList) <= 0:
            bankName = None
        else:
            bankName = tdList[0].string
        return bankName
        

    def parseBankAddress(self, bankDiv):
        addressDetails = bankDiv.find('td', string=re.compile(', CA'))
        if addressDetails is None:
            return
        addressNumber = addressDetails.previous_element.previous_sibling.string.strip()

        return addressNumber + addressDetails.string.strip()

    def parseBankHours(self, bankDiv):
        result = ""
        hours = bankDiv.find("b", string=re.compile('^Hours:'))
        if hours is not None:
            result = str(hours.parent)
        return result



    def parseBank(self, bankDiv):
        bankName = self.parseBankName(bankDiv)
        print(f"Bank Name: {bankName}")
        bankAddress = self.parseBankAddress(bankDiv)
        bankHours = self.parseBankHours(bankDiv)
        if bankName is None or bankAddress is None:
            return None, None

        bank = Bank(None, bankName, bankAddress, None, None, bankHours)



        bankId, coords, googleResponse = self.getBankGoogleInfo(bank)

        bank.id = bankId
        bank.lat = coords[0]
        bank.lng = coords[1]

        return bank, googleResponse


    def parseResultPage(self, html):
        soup = BeautifulSoup(html, "html.parser")
        resultsArticle = soup.article

        bankDivList = resultsArticle.find_all('div')
        with open(os.path.join(dataFolder, 'suntopiaGoogle.txt'), 'a') as f:
            responseDictList = []
            for bankDiv in bankDivList:
                bank, googleResponse = self.parseBank(bankDiv)
                if bank is None:
                    continue
                if not self.__isNoFetch:
                    responseDict = {hash(bank.name): googleResponse.json()}
                    responseDictList.append(responseDict)
                if bank is not None and bank.id not in self.bankIds:
                    self.bankIds.add(bank.id)
                    self.banks.add(bank)
            if not self.__isNoFetch:
                json.dump(responseDict, f)

    def getResultPage(self, num):
        urlParams = f"?page={num}"
        url = self.suntopiaPageUrl + urlParams
        response = requests.get(url)

        return response.text

    def getLatestBanks(self):
        if not self.__isNoFetch:
            with open(os.path.join(dataFolder, 'suntopiaGoogle.txt'), 'w') as f:
                pass
        with open(os.path.join(dataFolder, 'suntopia.txt'), 'w') as f:
            for pageNumber in range(self.startPage, self.endPage):
                print(f"Suntopia page {pageNumber}")
                resultHtml = self.getResultPage(pageNumber)
                f.write(f"{resultHtml}\n")
                self.parseResultPage(resultHtml)

        return self.banks, self.bankIds
