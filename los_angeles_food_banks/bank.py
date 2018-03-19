import json
import re
import os
from names import dataFolder
from cron import Cron
from openHours import OpenHours


class Bank(object):
    def __init__(self, id=None, name=None, address=None, lat=None, lng=None, hoursText=None):
        self.id = id
        self.name = name
        self.address = address
        self.lat = lat
        self.lng = lng
        self.hoursText = hoursText
        if hoursText is not None:
          print(hoursText)
          self.openHours = OpenHours(hoursText)

    def toJSON(self):
        obj = {"id": self.id,
               "name": self.name,
               "address": self.address,
               "lat": self.lat,
               "lng": self.lng,
               "hoursText": self.hoursText,
               "openHours": self.openHours.toJSON()}
        return obj