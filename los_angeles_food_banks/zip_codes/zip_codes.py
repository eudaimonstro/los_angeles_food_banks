import os
import subprocess
import requests
import json
import pprint

from names import GOOGLE_API_KEY
from names import dataFolder


class ZipCodes(object):
    def __init__(self, testing=False, nofetch=False):
        self.__isTesting = testing
        self.__isNoFetch = nofetch
        self.googleMapUrl = "https://maps.googleapis.com/maps/api/geocode/json"

        self.zipList = self.setZipList()
        self.zipCoordList = self.setZipCoordList()

        with open(os.path.join(dataFolder, 'zipCodeCoords.txt'), 'w') as z:
            [z.write(f"{coord}\n") for coord in self.zipCoordList]

    def getZipList(self):
        return self.__zipList

    def setZipList(self):
        with open(os.path.join(dataFolder, 'zip_codes.txt')) as z:
            zips = z.readlines()
        if self.__isTesting:
            zips = zips[0:5]
        return [x.strip() for x in zips]

    def getZipCoordList(self):
        if self.__isTesting:
            return self.__zipCoordList[0:5]
        else:
            return self.__zipCoordList

    def setZipCoordList(self):
        responseList = []
        results = []
        # with open(os.path.join(dataFolder, 'zipCodeCoordsGoogle.txt'), 'w') as z:
        with open(os.path.join(dataFolder, 'zipCodeCoordsGoogle.txt'), 'r') as z:
            zJson = json.load(z)["results"]
            for code in self.zipList:
                print(f"Zip Code: {code}")
                # urlParams = f"?address={str(code)}&key={GOOGLE_API_KEY}"
                # url = self.googleMapUrl + urlParams
                # googleResponse = requests.get(url)

                # responseDict = {code: googleResponse.json()}
                # json.dump(responseDict, z)

                # rJson = googleResponse.json()
                
                # pprint.pprint(zJson)
                rJson = zJson[code]
                coord = (rJson["results"][0]['geometry']['location']['lat'],
                         rJson['results'][0]['geometry']['location']['lng'])
                results.append(coord)

        return results