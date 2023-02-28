import ssl
from time import sleep
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
import cloudscraper
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton


class HaapiException(Exception):
    pass

class Haapi(metaclass=Singleton):
    MAX_CREATE_API_KAY_RETRIES = 5
    
    def __init__(self, apikey=None) -> None:
        self.url = "https://haapi.ankama.com"
        self.APIKEY = apikey
        self.login = None
        self.password = None
        self.certId = None
        self.certHash = None
    
    def setApiKey(self, apiKey):
        self.APIKEY = apiKey
        
    def getUrl(self, request):
        return self.url + {
            "CREATE_API_KEY": "/json/Ankama/v5/Api/CreateApiKey",
            "GET_LOGIN_TOKEN": "/json/Ankama/v5/Account/CreateToken",
        }[request]

    @property
    def clients(self):
        for client in [cloudscraper.create_scraper()]:
            yield client
    
    def createAPIKEY(self, login, password, certId, certHash, game_id=102) -> str:
        Logger().debug("[HAAPI] Sending http call to Create APIKEY")
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
        
        nbrtries = 0
        while nbrtries < self.MAX_CREATE_API_KAY_RETRIES:
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
                    Logger().debug("[HAAPI] APIKEY created")
                    key = response.json().get("key")
                    if key:
                        self.APIKEY = key
                        return response.json()
                    else:
                        if "reason" in response.json():
                            if response.json()["reason"] == "BAN":
                                raise HaapiException("[HAAPI] This account is banned definitively")
                        Logger().debug("[HAAPI] Error while calling HAAPI to get Login Token : %s" % response.content)
                        sleep(5)
                else:
                    Logger().debug(response.content.decode('UTF-8'))
                    from lxml import html
                    root = html.fromstring(response.content.decode('UTF-8'))
                    try:
                        error = root.xpath("//div[@class='cf-error-description']")[0].text
                        errorCode = root.xpath('//span[@class="cf-code-label"]//span')[0].text
                        Logger().debug(f"[HAAPI] error - {errorCode} : APIKEY creation for {login} failed for reason: {error}")
                    except IndexError:
                        Logger().debug(response.content.decode('UTF-8'))
                    sleep(5)
            Logger().debug("[HAAPI] Failed to create APIKEY, retrying in 10 seconds")
            sleep(10)
            nbrtries += 1
        return None
            
    def regenLoginToken(self):
        return self.getLoginToken(self.login, self.password, self.certId, self.certHash)
    
    def getLoginToken(self, certId, certHash, game_id=1, apiKey=None):
        Logger().debug("[HAAPI] Sending http call to get Login Token")
        self.APIKEY = apiKey
        if not self.APIKEY:
            raise HaapiException("[HAAPI] No haapi key found")
        nbrtries = 0
        while nbrtries < 5:
            for client in self.clients:
                try:
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
                        }
                    )
                    if response.headers["content-type"] == "application/json":
                        token = response.json().get("token")
                        if token:
                            Logger().debug("[HAAPI] Login Token created")
                            return token
                        else:
                            Logger().error("Error while calling HAAPI to get Login Token : %s" % response.json())
                            sleep(5)
                    else:
                        from lxml import html
                        root = html.fromstring(response.content.decode('UTF-8'))
                        error = root.xpath('//div[@id="what-happened-section"]//p/@text')
                        if error:
                            Logger().debug("Login Token creation failed, reason: %s" % error)
                        elif "The owner of this website (haapi.ankama.com) has banned you temporarily from accessing this website." in response.text:
                            Logger().debug("Login Token creation failed, reason: haapi.ankama.com has banned you temporarily from accessing this website.")
                        elif "Access denied | haapi.ankama.com used Cloudflare to restrict access" in response.text:
                            Logger().debug("Login Token creation failed, reason: haapi.ankama.com used Cloudflare to restrict access")
                        Logger().info("Login Token creation failed, retrying in 10 minutes")
                        sleep(60 * 10 + 3)
                except ssl.SSLError:
                    Logger().debug("[HAAPI] SSL error while calling HAAPI to get Login Token")
                    sleep(10)
                except ConnectionError:
                    Logger().error("No internet connection will try again in some seconds")
                    sleep(10)
                    
        return None