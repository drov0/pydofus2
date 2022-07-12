import json
from time import sleep
import httpx
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton

logger = Logger("Haapi")


class Haapi(metaclass=Singleton):
    
    def __init__(self) -> None:
        self.url = "https://haapi.ankama.com"
        self.APIKEY = None

    def getUrl(self, request):
        return self.url + {
            "CREATE_API_KEY": "/json/Ankama/v5/Api/CreateApiKey",
            "GET_LOGIN_TOKEN": "/json/Ankama/v5/Account/CreateToken",
        }[request]

    def createAPIKEY(self, login, password, certId, certHash, game_id=102) -> str:
        logger.debug("Calling HAAPI to Create APIKEY")
        data = {
            "login": login,
            "password": password,
            "game_id": game_id,
            "long_life_token": True,
            "certificate_id": str(certId),
            "certificate_hash": str(certHash),
            "shop_key": "ZAAP",
            "payment_mode": "OK",
        }
        response = httpx.post(
            self.getUrl("CREATE_API_KEY"),
            data=data,
            headers={
                "User-Agent": "Zaap",
                "Content-Type": "multipart/form-data",
            },
        )
        resposeJson = response.json()
        if "key" not in resposeJson:
            logger.error("Error while calling HAAPI to Create APIKEY")
            logger.error(resposeJson["message"])
            raise Exception(resposeJson["message"])
        self.APIKEY = resposeJson["key"]
        logger.debug("APIKEY created")
        return self.APIKEY


    def getLoginToken(self, login, password, certId, certHash, game_id=1):
        logger.debug("Calling HAAPI to get Login Token")
        if not self.APIKEY:
            self.createAPIKEY(login, password, certId, certHash)
        nbrTries = 0
        while nbrTries < 3:
            response = httpx.get(
                self.getUrl("GET_LOGIN_TOKEN"),
                params={
                    "game": game_id,
                    "certificate_id": certId,
                    "certificate_hash": certHash,
                },
                headers={
                    "User-Agent": "Zaap1",
                    "Content-Type": "multipart/form-data",
                    "APIKEY": self.APIKEY,
                },
            )
            try:
                token = response.json()["token"]
                logger.debug("Login Token created")
                return token
            except json.decoder.JSONDecodeError as e:
                import lxml.html

                root = lxml.html.parse(response.content)
                reason = root.xpath('//div[@id="what-happened-section"]//p/@text')[0]
                if (
                    reason
                    == "The owner of this website (haapi.ankama.com) has banned you temporarily from accessing this website."
                ):
                    logger.debug("Login Token creation failed, reason: %s" % reason)
                    logger.debug("Retrying in 60 seconds")
                    sleep(60)
            except KeyError as e:
                logger.error("Error while calling HAAPI to get Login Token")
                logger.error(response.content)
                raise Exception(e)
