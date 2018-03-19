# -*- coding: utf-8 -*-

"""Console script for los_angeles_food_banks."""
import sys
import subprocess
import json
import pprint
import os
from food_banks.la_food_bank import LAFoodBank
from food_banks.suntopia import Suntopia

from names import dataFolder


def main(args=None):
    testing = False
    nofetch = False
    if len(sys.argv) >= 2:
        if sys.argv[1] == "test":
            testing = True
        if len(sys.argv) >= 3:
            if sys.argv[2] == "nofetch":
                nofetch = True

    banksLA = LAFoodBank(testing, nofetch)
    laFoodBanks, laFoodBankIds = banksLA.getLatestBanks()

    suntopia = Suntopia(testing, nofetch, laFoodBankIds)
    suntopiaBanks, suntopiaBankIds = suntopia.getLatestBanks()

    banks = laFoodBanks.union(suntopiaBanks)

    with open(os.path.join(dataFolder, 'banks.json'), 'w+') as f:
        bankDump = [x.toJSON() for x in banks]
        json.dump(bankDump, f)

    bash = f"scp {dataFolder}banks.json droplet:/var/www/html/foodbanks"
    subprocess.run(bash.split())

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
