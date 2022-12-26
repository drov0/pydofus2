import json
import os
from pyd2bot.PyD2Bot import PyD2Bot

currdir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(currdir, "testData", "accounts.json"), "r") as fp:
    accounts = json.load(fp)
    
with open(os.path.join(currdir, "testData", "apiKeys.json"), "r") as fp:
    apiKeys = json.load(fp)

path_pioute_astrub = {
    "type": "RandomSubAreaFarmPath",
    "name": "pioute_astrub_village",
    "startVertex": {"mapId": 191104002, "mapRpZone": 1},
}
path_criniere_astrub = {
    "type": "RandomSubAreaFarmPath",
    "name": "pioute_astrub_village",
    "startVertex": {"mapId": 193332228, "mapRpZone": 1},
}
path_taniela = {
    "type": "RandomSubAreaFarmPath",
    "name": "pioute_astrub_village",
    "startVertex": {"mapId": 120062979, "mapRpZone": 1}
}
path_astrub_forest = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_astrub_forest",
    "startVertex": {"mapId": 189531139, "mapRpZone": 1}
}
path_astrub_egouts = {    
    "type": "RandomSubAreaFarmPath",
    "name": "path_astrub_egouts",
    "onlyDirections": False,
    "startVertex": {"mapId": 101715461, "mapRpZone": 1}
}
path_abraknyde_forest = {    
    "type": "RandomSubAreaFarmPath",
    "name": "path_abraknyde_forest",
    "startVertex": {"mapId": 147854595, "mapRpZone": 1}
}
path_champs_inglasse = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_champs_inglasse",
    "startVertex": {"mapId": 88083732, "mapRpZone": 1}
}
path_bonta_chaffer = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_bonta_chaffer",
    "startVertex": {"mapId": 158991365, "mapRpZone": 1}

}
path_blop_cania = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_blop_cania",
    "startVertex": {"mapId": 156240386, "mapRpZone": 1}
}
path_champs_astrub = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_champs_astrub",
    "startVertex": {"mapId": 189792777, "mapRpZone": 1}
}
path_campement_bworks = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_campement_bworks",
    "startVertex": {"mapId": 104073218, "mapRpZone": 1}
}
path_peninsule_gelees = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_peninsule_gelees",
    "startVertex": {"mapId": 88082952, "mapRpZone": 1}
}
path_dark_forest = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_dark_forest",
    "startVertex": {"mapId": 147851779, "mapRpZone": 1}
}
path_dragon_cochon = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_dragon_cochon",
    "startVertex": {"mapId": 72619522, "mapRpZone": 1}
}
path_mine_doeupole = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_mine_doeupole",
    "startVertex": {"mapId": 123470337, "mapRpZone": 1}
}
path_bord_foret_malefique = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_bord_foret_malefique",
    "startVertex": {"mapId": 88080650, "mapRpZone": 1}
}
path_egouts_astrubien = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_egouts_astrubien",
    "startVertex": {"mapId": 101715467, "mapRpZone": 1}
}
path_pic_cania = {
    "type": "RandomSubAreaFarmPath",
    "name": "path_pic_cania",
    "startVertex": {"mapId": 139462657, "mapRpZone": 1}
}

main_path = path_astrub_egouts

seller = {
    "name": "Maniaco-lalcolic",
    "id": 5820449062,
    "level": 62,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "slicer-the-dicer",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10095
}
leader = {
    "name": "Plusbellelavie",
    "id": 369475322150,
    "level": 65,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "melanco-lalco",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10098,
}
moneydicer = {
    "name": "Moneydicer",
    "id": 92638609702,
    "level": 70,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "Exodios-cra",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10097,
}
moneylife = {
    "name": "Moneylife",
    "id": 790823206,
    "level": 54,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "twistedFater",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10096,
}
hardlett = {
    "name": "Hardlett",
    "id": 76302254374,
    "level": 48,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "Money",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10094,
}
moneycreator = {
    "name": "Moneycreator",
    "id": 171988287782,
    "level": 61,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "Exodios-panda",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10093,
}
moneslicer = {
    "name": "Moneslicer",
    "id": 258718695718,
    "level": 49,
    "breedId": 10,
    "breedName": "Sadida",
    "serverId": 294,
    "serverName": "Merkator",
    "accountId": "Exodios-arc",
    "primarySpellId": 13516,
    "primaryStatId": 10,
    "serverPort": 10092,
}

plusbellelavieSession = {
    "key": "Plusbellelavie(369475322150)",
    "type": "fight",
    "unloadType": "seller",
    "character": leader,
    "path": main_path,
    "monsterLvlCoefDiff": 100,
    "seller": seller,
    "followers": [
        moneydicer,
        moneylife,
        hardlett,
        moneycreator,
        moneslicer
    ],
}
moneydicerSession = {
    "key": "Moneydicer(92638609702)",
    "type": "fight",
    "unloadType": "seller",
    "character": moneydicer,
    "leader": leader,
    "seller": seller,
}
moneylifeSession = {
    "key": "Moneylife(790823206)",
    "type": "fight",
    "unloadType": "seller",
    "character": moneylife,
    "leader": leader,
    "seller": seller,
}
hardlettSession = {
    "key": "Hardlett(76302254374)",
    "type": "fight",
    "unloadType": "seller",
    "character": hardlett,
    "leader": leader,
    "seller": seller,
}
moneycreatorSession = {
    "key": "Moneycreator(171988287782)",
    "type": "fight",
    "unloadType": "seller",
    "character": moneycreator,
    "leader": leader,
    "seller": seller,
}
moneslicerSession = {
    "key": "Moneslicer(258718695718)",
    "type": "fight",
    "unloadType": "seller",
    "character": moneslicer,
    "leader": leader,
    "seller": seller,
}
sellerSession = {
    "key": "Maniaco-lalcolic(5820449062)",
    "type": "selling",
    "unloadType": None,
    "character": seller
}
sessions = [plusbellelavieSession, moneydicerSession, moneylifeSession, hardlettSession, moneycreatorSession, moneslicerSession, sellerSession]

for session in sessions:
    accountId = session["character"]["accountId"]
    creds = accounts[accountId]
    apiKey = apiKeys[accountId]["key"]
    if apiKey is None:
        raise Exception("No API key for account {}".format(accountId))
    transport, client = PyD2Bot().runClient('localhost', session["character"]["serverPort"])
    client.runSession(creds["login"], creds["password"], creds["certId"], creds["certHash"], apiKey, json.dumps(session))
    