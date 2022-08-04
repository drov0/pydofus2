import json
import os
from time import sleep
from pyd2bot.PyD2Bot import PyD2Bot

currdir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(currdir, "testData", "accounts.json"), "r") as fp:
    accounts = json.load(fp)
with open(os.path.join(currdir, "testData", "apiKeys.json"), "r") as fp:
    apiKeys = json.load(fp)

plusbellelavieSession = {
    "key": "Plusbellelavie(336986964178)",
    "type": "fight",
    "unloadType": "seller",
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
    "seller": {
        "name": "Maniaco-lalcolic",
        "id": 336140370130,
        "level": 62,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "slicer-the-dicer",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10095,
    },
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
        {
            "name": "Hardlett",
            "id": 337022615762,
            "level": 48,
            "breedId": 10,
            "breedName": "Sadida",
            "serverId": 210,
            "serverName": "Merkator",
            "accountId": "Money",
            "primarySpellId": 13516,
            "primaryStatId": 10,
            "serverPort": 10094,
        },
        {
            "name": "Moneycreator",
            "id": 336919855314,
            "level": 61,
            "breedId": 10,
            "breedName": "Sadida",
            "serverId": 210,
            "serverName": "Merkator",
            "accountId": "Exodios-panda",
            "primarySpellId": 13516,
            "primaryStatId": 10,
            "serverPort": 10093,
        }
    ],
}
moneydicerSession = {
    "key": "Moneydicer(336815325394)",
    "type": "fight",
    "unloadType": "seller",
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
    "seller": {
        "name": "Maniaco-lalcolic",
        "id": 336140370130,
        "level": 62,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "slicer-the-dicer",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10095
    },
}
moneylifeSession = {
    "key": "Moneylife(336919920850)",
    "type": "fight",
    "unloadType": "seller",
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
    "seller": {
        "name": "Maniaco-lalcolic",
        "id": 336140370130,
        "level": 62,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "slicer-the-dicer",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10095
    },
}
hardlettSession = {
    "key": "Hardlett(337022615762)",
    "type": "fight",
    "unloadType": "seller",
    "character": {
        "name": "Hardlett",
        "id": 337022615762,
        "level": 48,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "Money",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10094,
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
    "seller": {
        "name": "Maniaco-lalcolic",
        "id": 336140370130,
        "level": 62,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "slicer-the-dicer",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10095
    },
}
moneyCreatorSession = {
    "key": "Moneycreator(336919855314)",
    "type": "fight",
    "unloadType": "seller",
    "character": {
        "name": "Moneycreator",
        "id": 336919855314,
        "level": 61,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "Exodios-panda",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10093,
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
    "seller": {
        "name": "Maniaco-lalcolic",
        "id": 336140370130,
        "level": 62,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "slicer-the-dicer",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10095
    },
}
sellerSession = {
    "key": "Maniaco-lalcolic(336140370130)",
    "type": "selling",
    "unloadType": None,
    "character": {
        "name": "Maniaco-lalcolic",
        "id": 336140370130,
        "level": 62,
        "breedId": 10,
        "breedName": "Sadida",
        "serverId": 210,
        "serverName": "Merkator",
        "accountId": "slicer-the-dicer",
        "primarySpellId": 13516,
        "primaryStatId": 10,
        "serverPort": 10095
    },
}
sessions = [plusbellelavieSession, moneydicerSession, moneylifeSession, hardlettSession, moneyCreatorSession, sellerSession]

for session in sessions:
    accountId = session["character"]["accountId"]
    creds = accounts[accountId]
    apiKey = apiKeys[accountId]["key"]
    if apiKey is None:
        raise Exception("No API key for account {}".format(accountId))
    transport, client = PyD2Bot().runClient('localhost', session["character"]["serverPort"])
    client.runSession(creds["login"], creds["password"], creds["certId"], creds["certHash"], apiKey, json.dumps(session))
    