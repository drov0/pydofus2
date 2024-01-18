import json
import os
import ssl
from time import sleep
from urllib.parse import urlencode

import aiohttp
import cloudscraper
import pyppeteer
import requests

from pydofus2.com.ankamagames.atouin.BrowserRequests import (BrowserRequests,
                                                             HttpError)
from pydofus2.com.ankamagames.atouin.HappiConfig import (AUTH_STATES,
                                                         ZAAP_CONFIG)
from pydofus2.com.ankamagames.atouin.ZaapError import ZaapError
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton


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
                "CREATE_API_KEY": "/json/Ankama/v4/Api/CreateApiKey",
                "GET_LOGIN_TOKEN": "/json/Ankama/v5/Account/CreateToken",
                "SIGN_ON": "/json/Ankama/v5/Account/SignOnWithApiKey",
                "SET_NICKNAME": "/json/Ankama/v5/Account/SetNicknameWithApiKey",
                "SEND_MAIL_VALIDATION": "/json/Ankama/v5/Account/SendMailValidation",
                "SECURITY_CODE": "/json/Ankama/v5/Shield/SecurityCode",
                "VALIDATE_CODE": "/json/Ankama/v5/Shield/ValidateCode",
                "DELETE_API_KEY": "/json/Ankama/v5/Api/DeleteApiKey",
                "CREATE_GUEST": "/json/Ankama/v2/Account/CreateGuest",
                "CREATE_TOKEN_WITH_PASSWORD": "/json/Ankama/v4/Account/CreateTokenWithPassword",
                "CREATE_TOKEN": "/json/Ankama/v4/Account/CreateToken",
                "GET_ACCESS_TOKEN": "/json/Ankama/v4/Account/GetAccessToken"
            }[request]
        )
        if params:
            result += "?" + urlencode(params)
        return result

    @classmethod
    async def create_apikey(cls, login, password, certId=None, certHash=None, game=102) -> str:
        Logger().debug("[HAAPI] Sending http call to Create APIKEY")
        data = {
            "login": login,
            "password": password,
            "game": game,
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
        except HttpError as e:
            if "reason" in e.body:
                print(f"error while creating api key: {json.dumps(e['body'])}")
                raise ZaapError({"codeError": f"haapi.{e['body']['reason']}", "error": e})
            Logger().error(f"Error while creating api key: {e}")
            raise e

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
    def getZaapVersion(cls):
        import yaml
        url = "https://launcher.cdn.ankama.com/installers/production/latest.yml?noCache=1hkaeforb"
        # Make an HTTP request to get the YAML file
        client = cloudscraper.create_scraper()
        response = client.get(
            url,
            headers={
                'user-Agent': "electron-builder",
                "cache-control": "no-cache",
                "sec-fetch-site": "none",
                "sec-fetch-mode": "no-cors",
                "sec-fetch-dest": "empty",
                'accept-encoding': 'identity',
                "accept-language": "en-US",
            },
        )

        if response.status_code != 200:
            raise Exception("Failed to download ZAAP version file")

        # Parse the YAML content
        try:
            data = yaml.safe_load(response.content)
        except yaml.YAMLError as e:
            return "Failed to parse YAML file"

        # Save the file locally
        local_folder = os.path.dirname(os.path.abspath(__file__))
        local_file_path = os.path.join(local_folder, 'latest.yml')
        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        # Extract the version
        version = data.get("version")
        if not version:
            raise Exception("Failed to extract ZAAP version from YAML file")
        
        return version

    @classmethod
    def getLoginTokenCloudScraper(cls, game_id, apiKey, certId='', certHash=''):
        nbrtries = 0
        client = cloudscraper.create_scraper()
        user_agent = f"Zaap {cls.getZaapVersion()}"
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
                        "apikey": apiKey,
                        "if-none-match": "null",
                        'user-Agent': user_agent,
                        'accept': '*/*',
                        'accept-encoding': 'gzip,deflate',
                        "sec-fetch-site": "none",
                        "sec-fetch-mode": "no-cors",
                        "sec-fetch-dest": "empty",
                        "accept-language": "en-US",
                    },
                )
                if response.headers["content-type"] == "application/json":
                    token = response.json().get("token")
                    if token:
                        Logger().debug("[HAAPI] Login Token created")
                        return token
                    elif response.json().get("reason") == "Certificate control failed.":
                        Logger().error("Invalid certificate, please check your certificate")
                        return None
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
                sleep(30)
            except Exception:
                Logger().error("No internet connection will try again in some seconds")
                sleep(30)
        
    @classmethod
    async def create_token_with_password(cls, login, password, game):
        url = cls.getUrl("CREATE_TOKEN_WITH_PASSWORD")
        data = {
            "login": login,
            "password": password,
            "game": game
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        body = await response.json()
                        return body  # or whatever part of the response you need
                    else:
                        error_details = await response.text()  # Get more details from the response
                        Logger().error(f"Error creating token: {response.status}, {error_details}")
                        return None
            except Exception as e:
                Logger().error(f"Exception occurred: {e}")
                raise e
            
    @classmethod
    async def create_token(cls, login, password, certificate_id, certificate_hash, game):
        url = cls.getUrl("CREATE_TOKEN")
        data = {
            "login": login,
            "password": password,
            "certificate_id": certificate_id,
            "certificate_hash": certificate_hash,
            "game": game
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, data=data) as response:
                    if response.status == 200:
                        body = await response.json()
                        return body  # or whatever part of the response you need
                    else:
                        error_details = await response.text()  # Get more details from the response
                        Logger().error(f"Error creating token: {response.status}, {error_details}")
                        return None
            except Exception as e:
                Logger().error(f"Exception occurred: {e}")
                raise e
            
    @classmethod
    async def get_access_token(cls, login, password, game):
        url = cls.getUrl(
            "GET_ACCESS_TOKEN",
            {
                "login": login,
                "password": password,
                "game": game
            }
        )

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        body = await response.json()
                        return body  # or whatever part of the response you need
                    else:
                        error_details = await response.text()  # Get more details from the response
                        Logger().error(f"Error creating token: {response.status}, {error_details}")
                        return None
            except Exception as e:
                Logger().error(f"Exception occurred: {e}")
                raise e


if __name__ == "__main__":
    r = Haapi.getZaapVersion()
    print(r)
    