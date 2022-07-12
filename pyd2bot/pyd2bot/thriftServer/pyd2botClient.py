import json
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService


if __name__ == '__main__':
    transport = TSocket.TSocket('127.0.0.1', 9999)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Pyd2botService.Client(protocol)
    transport.open()
    session = {
        "name":"sadida-leader",
        "characterId":336986964178,
        "spellId":13516,
        "pathId":"pioute_astrub_village",
        "followers":["Moneydicer"],
        "statToUp":10,
        "isLeader":True,
        "character":{
            "characterName":"Plusbellelavie",
            "accountId":"melanco-lalco",
            "characterId":336986964178,
            "serverId":210
        },
        "path":{
            "type":"RandomSubAreaFarmPath",
            "name":"pioute_astrub_village",
            "subAreaId":95,
            "startVertex":{
                "mapId":191104002,
                "mapRpZone":1
            },
            "fightOnly":True,
            "monsterLvlCoefDiff":3,
            "jobIds":[]
        }
    }
    sessionStr = json.dumps(session)
    recv = client.fetchAccountCharacters(
        "maniac.depressif@gmail.com", 
        "5hgCd.JMUVwxK-s", 
        126142784, 
        "aed578dee4dbb4aec9ddab79dedb14b91ed5c40313e846e1fb80616051f39aa5"
    )
    # recv = client.runSession(
    #     "maniac.depressif@gmail.com", 
    #     "5hgCd.JMUVwxK-s", 
    #     126142784, 
    #     "aed578dee4dbb4aec9ddab79dedb14b91ed5c40313e846e1fb80616051f39aa5",
    #     sessionStr
    # )
    print(recv)
    transport.close()