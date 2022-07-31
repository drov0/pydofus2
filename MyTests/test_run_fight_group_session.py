import json
import os
from time import sleep
from pyd2bot.PyD2Bot import PyD2Bot

currdir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(currdir, "testData", "accounts.json"), "r") as fp:
    accounts = json.load(fp)
with open(os.path.join(currdir, "testData", "apiKeys.json"), "r") as fp:
    _apiKeys = json.load(fp)

plusbellelavieSession = {
    "key": "Plusbellelavie(336986964178)",
    "type": "fight",
    "character": {
        "name": "Plusbellelavie",
        "id": 336986964178,
        "level": 65,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "melanco-lalco",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10098,
    },
    "path": {
        "type": "RandomSubAreaFarmPath",
        "name": "pioute_astrub_village",
        "subAreaId": 95,
        "startVertex": {"mapId": 191104002, "mapRpZone": 1},
        "fightOnly": True,
        "monsterLvlCoefDiff": 3
    },
    "monsterLvlCoefDiff": "3",
    "followers": [
        {
            "name": "Moneydicer",
            "id": 336815325394,
            "level": 70,
            "breedId": 10,
            "breedName": "Sadida",
            "serverId": 210,
            "serverName": "Merkator",
            "accountId": "Exodios-cra",
            "primarySpellId": 13516,
            "primaryStatId": 10,
            "serverPort": 10097,
        },
        {
            "name": "Moneylife",
            "id": 336919920850,
            "level": 54,
            "breedId": 10,
            "breedName": "Sadida",
            "serverId": 210,
            "serverName": "Merkator",
            "accountId": "twistedFater",
            "primarySpellId": 13516,
            "primaryStatId": 10,
            "serverPort": 10096,
        },
    ],
}
moneydicerSession = {
    "key": "Moneydicer(336815325394)",
    "type": "fight",
    "character": {
        "name": "Moneydicer",
        "id": 336815325394,
        "level": 70,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "Exodios-cra",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10097,
    },
    "leader": {
        "name": "Plusbellelavie",
        "id": 336986964178,
        "level": 65,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "melanco-lalco",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10098,
    },
}
moneylifeSession = {
    "key": "Moneylife(336919920850)",
    "type": "fight",
    "character": {
        "name": "Moneylife",
        "id": 336919920850,
        "level": 54,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "twistedFater",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10096,
    },
    "leader": {
        "name": "Plusbellelavie",
        "id": 336986964178,
        "level": 65,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "melanco-lalco",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10098,
    },
}

sessions = [plusbellelavieSession, moneydicerSession, moneylifeSession]

for session in sessions:
    accountId = session["character"]["accountId"]
    creds = accounts[accountId]
    transport, client = PyD2Bot().runClient('localhost', session["character"]["serverPort"])
    session["APIKEY"] = _apiKeys[accountId]["key"]
    client.runSession(creds["login"], creds["password"], creds["certId"], creds["certHash"], json.dumps(session))
    