import requests
import pprint
import os
import json
from bank import Bank
from zip_codes.zip_codes import ZipCodes
from names import GOOGLE_API_KEY
from names import dataFolder

global GOOGLE_API_KEY
class LAFoodBank:
    def __init__(self, testing=False, nofetch=False, idList=set()):
        self.__isTesting = testing
        self.__isNoFetch = nofetch
        self.laFoodBankPageUrl = "https://www.lafoodbank.org/wp-admin/admin-ajax.php"
        self.googleMapsUrl = "https://maps.googleapis.com/maps/api/geocode/json"
        self.laFoodBankIds = set()
        self.bankIds = set()
        self.banks = set()
        self.zipCodeCoords = ZipCodes(self.__isTesting).zipCoordList
        self.responseBanksJsonList = self.getBanksFromLAFoodBank()

        if self.__isTesting:
            self.responseBanksJsonList = self.responseBanksJsonList[0:10]

    def getBanksFromLAFoodBank(self):
        results = []
        with open(os.path.join(dataFolder, 'LAFoodBank.txt'), 'w') as f:
            for coord in self.zipCodeCoords:
                print(f"LA Food Bank for coord: {coord}")
                response = self.getBanksByZipLatLng(coord)
                if response is None or response.json() is None or response.json() == '':
                    continue
                rJson = response.json()
                for bank in rJson:
                    if bank['id'] not in self.laFoodBankIds:
                        self.laFoodBankIds.add(bank['id'])
                        results.append(bank)
                #     f.write(f"{response.json()}\n")
                # results = results + response.json()
        return results

    def getBanksByZipLatLng(self, coord):
        urlParams1 = f"?action=store_search&lat={coord[0]}&lng={coord[1]}"
        urlParams2 = "&max_results=25&search_radius=15"
        url = f"{self.laFoodBankPageUrl}{urlParams1}{urlParams2}"

        response = requests.get(url)

        return response

    def parseResponseJsonList(self):
        responseGoogleInfo = []
        with open(os.path.join(dataFolder, 'LAFoodBankGoogle.json'), 'a') as f:
            responseDictList = []
            for bankJson in self.responseBanksJsonList:
                bank = self.parseResponseJson(bankJson)
                bankId, infoJson = self.getBankGoogleInfo(bank)
                if not self.__isNoFetch:
                    responseDict = {hash(bank.name): infoJson}
                    responseDictList.append(responseDict)
                if bank.id is not None and bank.id not in self.bankIds:
                    self.bankIds.add(bank.id)
                    self.banks.add(bank)
            if not self.__isNoFetch:
                json.dump(responseDictList, f)


    def parseResponseJson(self, bankJson):
        bankName = bankJson['store']
        bankAddress = bankJson['address'] + " " + bankJson['city'] + " " + bankJson['state']
        bankHours = bankJson['fax']
        bankLat = bankJson['lat']
        bankLng = bankJson['lng']
        return Bank(None, bankName, bankAddress, bankLat, bankLng, bankHours)

    def getBankGoogleInfo(self, bank):
        if self.__isNoFetch:
            print(bank.__dict__)
            with open(os.path.join(dataFolder, 'LAFoodBankGoogle.json'), 'r') as f:
                storedResponses = json.load(f)
                return storedResponses[0][hash(bank.name)]
        urlParams = f"?address={bank.name + bank.address}&key={GOOGLE_API_KEY}"
        url = self.googleMapsUrl + urlParams

        response = requests.get(url)

        infoJson = response.json()

        if(len(infoJson['results'])) > 1:
            bankId = None
        elif(len(infoJson['results'])) < 1:
            bankId = None
        else:
            bankId = infoJson['results'][0]['place_id']
        bank.id = bankId
        return bankId, infoJson

    def update(self):
        pass

    def getLatestBanks(self):
        self.parseResponseJsonList()
        return self.banks, self.bankIds
