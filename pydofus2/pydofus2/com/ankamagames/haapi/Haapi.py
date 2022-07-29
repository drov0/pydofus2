import json
from time import sleep
import httpx
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton

logger = Logger()


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
            "lang" : "fr"
        }
        nbrTries = 0
        with httpx.Client(http2=True) as client:
            while nbrTries < 3:
                response = client.post(
                    self.getUrl("CREATE_API_KEY"),
                    data=data,
                    headers={
                        "User-Agent": "Zaap 3.6.2",
                        "Content-Type": "multipart/form-data",
                        "cache-control": "no-cache",
                    },
                )
                print(response.http_version)
                try:
                    key = response.json()["key"]
                    self.APIKEY = key
                    return key
                except json.decoder.JSONDecodeError as e:
                    from lxml import html
                    root = html.fromstring(response.content.decode('UTF-8'))
                    error = root.xpath('//span[@class="error-description"]')[0].text
                    errorCode = root.xpath('//span[@class="code-label"]//span')[0].text
                    logger.debug(f"Login Token creation for login {login} failed, reason: %s\nerror code %s" % (error, errorCode))
                    logger.debug("Retrying in 2 minutes")
                    raise
                    # sleep(2 * 60)
                except KeyError as e:
                    logger.debug("Error while calling HAAPI to get Login Token")
                    logger.debug(response.content)
                    raise Exception(e)


    def getLoginToken(self, login, password, certId, certHash, game_id=1):
        logger.debug("Calling HAAPI to get Login Token")
        if not self.APIKEY:
            self.createAPIKEY(login, password, certId, certHash)
        nbrTries = 0
        with httpx.Client(http2=True) as client:
            while nbrTries < 3:
                response = client.get(
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
                logger.debug(response.content)
                try:
                    token = response.json()["token"]
                    logger.debug("Login Token created")
                    return token
                except json.decoder.JSONDecodeError as e:
                    from lxml import html
                    root = html.fromstring(response.content.decode('UTF-8'))
                    error = root.xpath('//div[@id="what-happened-section"]//p/@text')[0]
                    if (
                        error
                        == "The owner of this website (haapi.ankama.com) has banned you temporarily from accessing this website."
                    ):
                        logger.debug("Login Token creation failed, reason: %s" % error)
                        logger.debug("Retrying in 60 seconds")
                        raise Exception(error)
                except KeyError as e:
                    logger.error("Error while calling HAAPI to get Login Token")
                    logger.error(response.content)
                    raise Exception(e)
