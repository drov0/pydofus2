import json
import os
from pydofus2.com.ankamagames.haapi.Haapi import Haapi

currdir = os.path.dirname(os.path.abspath(__file__))

accountsf = open(os.path.join(currdir, "Bot_sessions", "testData", "accounts.json"), "r")
resultf = open(os.path.join(currdir, "Bot_sessions", "testData", "result.json"), "w")

accounts : dict = json.load(accountsf)

Apikeys = {}
for key, account in accounts.items():
    response = Haapi().createAPIKEY(account["login"], account["password"], account["certId"], account["certHash"])
    Apikeys[key] = response

json.dump(Apikeys, resultf)