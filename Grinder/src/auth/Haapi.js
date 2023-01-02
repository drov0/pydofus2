class RESTClient {


    HttpError = function (e, t) {
        Error.captureStackTrace(this, this.constructor), this.statusCode = e.status, this.message = "Http request failed", this.body = t
    };

    async request(url, request) {
        request.timeout = 5e3;
        request.headers = {
            "User-Agent": "Zaap 3.6.2",
            "content-type": "multipart/form-data",
        };

        console.log(request);
        process.env.DEBUG_NETWORK && console.log("[HTTP] answer", request.method, url);
        const res = await fetch(url, request);
        let textResponse = await res.text();
        if (process.env.DEBUG_NETWORK && console.log("[HTTP] result", request.method, url, res.status, res.statusText), res.status >= 400) {
            throw "application/json" === res.headers.get("content-type") && (res.body = textResponse = JSON.parse(textResponse)), new this.HttpError(textResponse);
        }
        const l = res.headers && res.headers.get("content-type") && "application/json" === res.headers.get("content-type");
        return 204 !== res.status && l && (textResponse = JSON.parse(textResponse)), res.body = textResponse, res
    }

    async get(e, t = {}) {
        return this.request(e, {
            method: "GET",
            headers: {
                "If-None-Match": null,
                ...t
            }
        })
    }

    post(url, body, headers = {}) {
        const r = headers.hasOwnProperty("Content-Type") && "application/json" === headers["Content-Type"];
        return this.request(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: headers
        })
    }

    put(e, t, n = {}) {
        const r = n.hasOwnProperty("Content-Type") && "application/json" === n["Content-Type"];
        return this.request(e, {
            method: "PUT",
            body: r ? JSON.stringify(t) : s.stringify(t),
            headers: n
        })
    }

    delete(e, t = {}) {
        return this.request(e, {
            method: "DELETE",
            headers: t
        })
    }
}


class Haapi {

    constructor() {
        this.haapiUrl = "https://haapi.ankama.com/";
        this.authHelper = require('./AuthHelper.js').instance;
        this.restClient = new RESTClient();
    }

    getUrl(requestName, body) {
        let url = this.haapiUrl + {
            ANKAMA_ACCOUNT_ACCOUNT: "json/Ankama/v5/Account/Account",
            ANKAMA_ACCOUNT_CREATE_TOKEN: "json/Ankama/v5/Account/CreateToken",
            ANKAMA_ACCOUNT_ORIGIN_WITH_API_KEY: "json/Ankama/v5/Account/OriginWithApiKey",
            ANKAMA_ACCOUNT_SEND_DEVICE_INFOS: "json/Ankama/v5/Account/SendDeviceInfos",
            ANKAMA_ACCOUNT_SEND_MAIL_VALIDATION: "json/Ankama/v5/Account/SendMailValidation",
            ANKAMA_ACCOUNT_SET_EMAIL: "json/Ankama/v5/Account/SetEmail",
            ANKAMA_ACCOUNT_SET_NICKNAME_WITH_API_KEY: "json/Ankama/v5/Account/SetNicknameWithApiKey",
            ANKAMA_ACCOUNT_SIGN_ON_WITH_API_KEY: "json/Ankama/v5/Account/SignOnWithApiKey",
            ANKAMA_ACCOUNT_SET_IDENTITY_WITH_API_KEY: "json/Ankama/v5/Account/SetIdentityWithApiKey",
            ANKAMA_ACCOUNT_STATUS: "json/Ankama/v5/Account/Status",
            ANKAMA_API_CREATE_API_KEY: "json/Ankama/v5/Api/CreateApiKey",
            ANKAMA_API_DELETE_API_KEY: "json/Ankama/v5/Api/DeleteApiKey",
            ANKAMA_API_REFRESH_API_KEY: "json/Ankama/v5/Api/RefreshApiKey",
            ANKAMA_CMS_ITEMS_GET: "json/Ankama/v5/Cms/Items/Get",
            ANKAMA_CMS_ITEMS_CAROUSEL_GET: "json/Ankama/v5/Cms/Items/Carousel/GetForLauncher",
            ANKAMA_CMS_ITEMS_GETBYID: "json/Ankama/v5/Cms/Items/GetById",
            ANKAMA_CMS_POLLINGAME_GET: "json/Ankama/v5/Cms/PollInGame/Get",
            ANKAMA_CMS_POLLINGAME_MARKASREAD: "json/Ankama/v5/Cms/PollInGame/MarkAsRead",
            ANKAMA_GAME_END_SESSION_WITH_API_KEY: "json/Ankama/v5/Game/EndSessionWithApiKey",
            ANKAMA_GAME_LIST_WITH_API_KEY: "json/Ankama/v5/Game/ListWithApiKey",
            ANKAMA_GAME_SEND_EVENTS: "json/Ankama/v5/Game/SendEvents",
            ANKAMA_GAME_START_SESSION_WITH_API_KEY: "json/Ankama/v5/Game/StartSessionWithApiKey",
            ANKAMA_LEGALS_SET_TOU_VERSION: "json/Ankama/v5/Legals/SetTouVersion",
            ANKAMA_LEGALS_TOU: "json/Ankama/v5/Legals/Tou",
            ANKAMA_MONEY_OGRINS_AMOUNT: "json/Ankama/v5/Money/OgrinsAmount",
            ANKAMA_PREMIUM_GAME_CONNECT: "json/Ankama/v5/Game/Premium/Session/Connect",
            ANKAMA_PREMIUM_GAME_DISCONNECT: "json/Ankama/v5/Game/Premium/Session/Disconnect",
            ANKAMA_PROVIDER_API_KEY_LINK: "json/Ankama/v5/Provider/ApiKeyLink",
            ANKAMA_PROVIDER_API_KEY_LOGIN: "json/Ankama/v5/Provider/ApiKeyLogin",
            ANKAMA_PROVIDER_GHOST_CREATE: "json/Ankama/v5/Provider/ApiKeyGhostCreate",
            ANKAMA_SHIELD_SECURITY_CODE: "json/Ankama/v5/Shield/SecurityCode",
            ANKAMA_SHIELD_VALIDATE_CODE: "json/Ankama/v5/Shield/ValidateCode",
            ANKAMA_SHOP_ARTICLES_LIST_BY_CATEGORY: "json/Ankama/v5/Shop/ArticlesListByCategory",
            ANKAMA_SHOP_CATEGORIES_LIST: "json/Ankama/v5/Shop/CategoriesList",
            ANKAMA_SHOP_SIMPLE_BUY: "json/Ankama/v5/Shop/SimpleBuy",
            ANKAMA_SHOP_ARTICLE_LIST_BY_ID: "json/Ankama/v5/Shop/ArticlesListByIds",
            ANKAMA_VOD_ACCESS_TOKEN_GET: "json/Ankama/v5/Vod/AccessToken/GetAccessToken"
        }[requestName];
        const s = JSON.stringify(body);
        return s && (url += "?" + s), url
    }

    createAccountToken(e, t, n) {
        e.exports = async function (e, game_id, n, certificate_id, certificate_hash) {
            getTokenUrl = this.getUrl("ANKAMA_ACCOUNT_CREATE_TOKEN", {
                game: game_id,
                certificate_id: certificate_id,
                certificate_hash: certificate_hash
            });
            try {
                return (await RESTClient.get(getTokenUrl, { APIKEY: n.key })).body.token
            } catch (e) {
                throw i.error("Error when creating token for game", n.accountId, e), 403 === e.statusCode && await r.instance.logoutAccount(n), e
            }
        }
    }

    async getAPIKey(login, password, certId, certHash) {
        var cert = this.authHelper.getStoredCertificate(login).certificate;
        var certificate_hash = this.authHelper.generateHashFromCertif(cert);
        let url = this.getUrl("ANKAMA_API_CREATE_API_KEY");
        try {
            const {
                body: body
            } = await this.restClient.post(url, {
                login: login,
                password: password,
                game_id: 102,
                long_life_token: true,
                shop_key: "ZAAP",
                payment_mode: "OK",
                lang: "fr",
                certificate_id: cert.id,
                certificate_hash: certificate_hash
            });
            return {
                key: body.key,
                accountId: body.account_id,
                refreshToken: body.refresh_token,
                security: body.data && body.data.security_state,
                reason: body.data && body.data.security_detail
            }
        } catch (e) {
            if (e.body && e.body.reason) throw new Error({
                codeError: "haapi." + e.body.reason,
                error: e
            });
            throw e;
        }
    }
}

Haapi.getAPIKey("tarik-maj@hotmail.fr", "rmrtxha1", 126304780, "f2a5726c0581d18c92b4a2278ff4c457240e62e8a64265cef8793781c641ba8c")