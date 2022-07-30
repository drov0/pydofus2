import json
from time import sleep
import httpx
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from requests import request
import requests
import cloudscraper

logger = Logger()
class HaapiException(Exception):
    pass

class Haapi(metaclass=Singleton):
    
    def __init__(self) -> None:
        self.url = "https://haapi.ankama.com"
        self.APIKEY = None

    def getUrl(self, request):
        return self.url + {
            "CREATE_API_KEY": "/json/Ankama/v5/Api/CreateApiKey",
            "GET_LOGIN_TOKEN": "/json/Ankama/v5/Account/CreateToken",
        }[request]

    @property
    def clients(self):
        for client in [
            cloudscraper.create_scraper(),
            cloudscraper.create_scraper(disableCloudflareV1=True),
            cloudscraper.create_scraper(interpreter='nodejs'),
            cloudscraper.create_scraper(allow_brotli=False),
            httpx.Client(http2=True),
            httpx.Client()]:
            yield client
    
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
        for client in self.clients:
            response = client.post(
                self.getUrl("CREATE_API_KEY"),
                data=data,
                headers={
                    "User-Agent": "Zaap 3.6.2",
                    "Content-Type": "multipart/form-data",
                    "cache-control": "no-cache",
                },
            )
            if response.headers["content-type"] == "application/json":
                logger.debug("APIKEY created")
                key = response.json().get("key")
                if key:
                    self.APIKEY = key
                    return key
                else:
                    logger.debug("Error while calling HAAPI to get Login Token : %s" % response.content)
                    sleep(5)
            else:
                from lxml import html
                root = html.fromstring(response.content.decode('UTF-8'))
                error = root.xpath('//span[@class="error-description"]')[0].text
                errorCode = root.xpath('//span[@class="code-label"]//span')[0].text
                logger.debug(f"[Haapi error {errorCode}] : Login Token creation for login {login} failed for reason: {error}")
                sleep(5)
        return None
    
    def getLoginToken(self, login, password, certId, certHash, game_id=1):
        logger.debug("Calling HAAPI to get Login Token")
        nbrtries = 0
        while nbrtries < 5:
            self.APIKEY = self.createAPIKEY(login, password, certId, certHash)
            if not self.APIKEY:
                logger.debug("Fail to create APIKEY, retrying in 30 seconds")
                sleep(30)
                nbrtries += 1
            else:
                break
        if not self.APIKEY:
            raise HaapiException("Failed to create APIKEY")
        nbrtries = 0
        while nbrtries < 5:
            for client in self.clients:
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
                if response.headers["content-type"] == "application/json":
                    token = response.json().get("token")
                    if token:
                        logger.debug("Login Token created")
                        return token
                    else:
                        logger.error("Error while calling HAAPI to get Login Token : %s" % response.json()["message"])
                        sleep(5)
                else:
                    from lxml import html
                    root = html.fromstring(response.content.decode('UTF-8'))
                    error = root.xpath('//div[@id="what-happened-section"]//p/@text')[0]
                    logger.debug("Login Token creation failed, reason: %s" % error)
                    sleep(5)
        return None
