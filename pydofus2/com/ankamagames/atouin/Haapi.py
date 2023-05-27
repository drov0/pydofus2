import json
import os
import ssl
from urllib.parse import urlencode
from time import sleep
import pyppeteer
import requests
from pydofus2.com.ankamagames.atouin.BrowserRequests import BrowserRequests
from pydofus2.com.ankamagames.atouin.HappiConfig import AUTH_STATES, ZAAP_CONFIG
from pydofus2.com.ankamagames.atouin.ZaapError import ZaapError
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
import cloudscraper


class HaapiException(Exception):
    pass


class Haapi:
    MAX_CREATE_API_KAY_RETRIES = 5
    url = "https://haapi.ankama.com"

    @classmethod
    def getUrl(cls, request, params={}):
        result = (
            cls.url
            + {
                "CREATE_API_KEY": "/json/Ankama/v5/Api/CreateApiKey",
                "GET_LOGIN_TOKEN": "/json/Ankama/v5/Account/CreateToken",
                "SIGN_ON": "/json/Ankama/v5/Account/SignOnWithApiKey",
                "SET_NICKNAME": "/json/Ankama/v5/Account/SetNicknameWithApiKey",
                "SEND_MAIL_VALIDATION": "/json/Ankama/v5/Account/SendMailValidation",
                "SECURITY_CODE": "/json/Ankama/v5/Shield/SecurityCode",
                "VALIDATE_CODE": "/json/Ankama/v5/Shield/ValidateCode",
                "DELETE_API_KEY": "/json/Ankama/v5/Api/DeleteApiKey",
                "CREATE_GUEST": "/json/Ankama/v2/Account/CreateGuest",
            }[request]
        )
        if params:
            result += "?" + urlencode(params)
        return result

    @classmethod
    async def createAPIKEY(cls, login, password, certId=None, certHash=None, game_id=102) -> str:
        Logger().debug("[HAAPI] Sending http call to Create APIKEY")
        data = {
            "login": login,
            "password": password,
            "game_id": game_id,
            "long_life_token": True,
            "shop_key": "ZAAP",
            "payment_mode": "OK",
            "lang": "fr",
        }
        if certId:
            data["certificate_id"] = str(certId)
            data["certificate_hash"] = str(certHash)
        try:
            response = await BrowserRequests.post(cls.getUrl("CREATE_API_KEY"), data=data)
            body = response["body"]
            cls.APIKEY = body.get("key")
            return {
                "key": body["key"],
                "accountId": body["account_id"],
                "refreshToken": body["refresh_token"],
                "security": body["data"]["security_state"]
                if "data" in body and "security_state" in body["data"]
                else None,
                "reason": body["data"]["security_detail"]
                if "data" in body and "security_detail" in body["data"]
                else None,
                "expirationDate": body["expiration_date"],
            }
        except Exception as e:
            if "body" in e and "reason" in e["body"]:
                print(f"error while creating api key: {json.dumps(e['body'])}")
                raise ZaapError({"codeError": f"haapi.{e['body']['reason']}", "error": e})
            elif e["statusCode"] == 403:
                raise ZaapError({"error": e})

    @classmethod
    async def getLoginToken(cls, certId, certHash, game_id, apiKey):
        Logger().debug("Sending http call to get Login Token")
        url = cls.getUrl(
            "GET_LOGIN_TOKEN",
            {
                "game": game_id,
                "certificate_id": certId,
                "certificate_hash": certHash,
            },
        )
        resp = await BrowserRequests.get(
            url,
            headers={
                "APIKEY": apiKey,
            },
        )
        token = resp["body"]["token"]
        Logger().debug(f"Generated Login Token : {token}")
        return resp["body"]["token"]

    @classmethod
    async def createGuest(cls, gameId=17, lang="en"):
        url = cls.getUrl("CREATE_GUEST", {"game": gameId, "lang": lang})
        resp = await BrowserRequests.get(url)
        return resp["body"]

    @classmethod
    async def shieldSecurityCode(cls, apikey, bySMS=False):
        url = cls.getUrl("SECURITY_CODE", {"transportType": "SMS" if bySMS else "EMAIL"})
        resp = await BrowserRequests.get(url, {"apikey": apikey})
        return resp["body"]["domain"]

    @classmethod
    async def shieldValidateCode(cls, apikey, validationCode, hm1, hm2):
        userName = f"launcher-{os.getlogin()}"
        url = cls.getUrl(
            "VALIDATE_CODE",
            {"game_id": ZAAP_CONFIG.ZAAP_GAME_ID, "code": validationCode, "hm1": hm1, "hm2": hm2, "name": userName},
        )
        try:
            response = await BrowserRequests.get(url, {"apikey": apikey})
            return response["body"]
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.text:
                error = json.loads(e.response.text)
                if error["message"] == "ALREADYSECURED":
                    raise Exception("ALREADYSECURED")
                raise ZaapError({"codeError": f"haapi.{error['message']}", "error": e})
            raise ZaapError({"codeError": "haapi.CODEPROBLEM", "complement": e})

    @classmethod
    async def signOnWithApikey(cls, game_id, apikey):
        result = await BrowserRequests.post(cls.getUrl("SIGN_ON"), data={"game": game_id}, headers={"APIKEY": apikey})
        body = result["body"]
        if body["account"]["locked"] == ZAAP_CONFIG.USER_ACCOUNT_LOCKED.MAILNOVALID:
            Logger().error("[AUTH] Mail not confirmed by user")
            raise Exception(AUTH_STATES.USER_EMAIL_INVALID)
        return {"id": str(body["id"]), "account": cls.parseAccount(body["account"])}

    @classmethod
    async def setNickname(cls, nickname, apikey, lang="en"):
        url = cls.getUrl("SET_NICKNAME")
        res = await BrowserRequests.post(url, {"nickname": nickname, "lang": lang}, {"apikey": apikey})
        return res["body"]

    @classmethod
    async def deleteApikey(cls, apikey):
        url = cls.getUrl("DELETE_API_KEY")
        try:
            return await BrowserRequests.get(url, {"apikey": apikey})
        except pyppeteer.errors.PageError:
            return True

    @classmethod
    def parseAccount(cls, body):
        return {
            "id": body["id"],
            "type": body["type"],
            "login": body["login"],
            "nickname": body["nickname"],
            "firstname": body["firstname"],
            "lastname": body["lastname"],
            "nicknameWithTag": f"{body['nickname']}#{body['tag']}",
            "tag": body["tag"],
            "security": body["security"],
            "addedDate": body["added_date"],
            "locked": body["locked"],
            "parentEmailStatus": body["parent_email_status"],
            "avatar": body["avatar_url"],
        }

    @classmethod
    def getLoginTokenCloudScraper(cls, certId, certHash, game_id, apiKey):
        nbrtries = 0
        client = cloudscraper.create_scraper()
        while nbrtries < 5:
            try:
                url = cls.getUrl(
                    "GET_LOGIN_TOKEN",
                    {
                        "game": game_id,
                        "certificate_id": certId,
                        "certificate_hash": certHash,
                    },
                )
                response = client.get(
                    url,
                    headers={
                        'User-Agent': 'Zaap 3.9.3',
                        'accept': '*/*',
                        'accept-encoding': 'gzip,deflate',
                        "APIKEY": apiKey,
                    },
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

                    root = html.fromstring(response.content.decode("UTF-8"))
                    error = root.xpath('//div[@id="what-happened-section"]//p/@text')
                    if error:
                        Logger().debug("Login Token creation failed, reason: %s" % error)
                    elif (
                        "The owner of this website (haapi.ankama.com) has banned you temporarily from accessing this website."
                        in response.text
                    ):
                        Logger().debug(
                            "Login Token creation failed, reason: haapi.ankama.com has banned you temporarily from accessing this website."
                        )
                    elif "Access denied | haapi.ankama.com used Cloudflare to restrict access" in response.text:
                        Logger().debug(
                            "Login Token creation failed, reason: haapi.ankama.com used Cloudflare to restrict access"
                        )
                    Logger().info("Login Token creation failed, retrying in 10 minutes")
                    sleep(60 * 10 + 3)
            except ssl.SSLError:
                Logger().debug("[HAAPI] SSL error while calling HAAPI to get Login Token")
                sleep(10)
            except ConnectionError:
                Logger().error("No internet connection will try again in some seconds")
                sleep(10)
