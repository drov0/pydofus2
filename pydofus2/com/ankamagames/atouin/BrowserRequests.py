import asyncio
import json
from urllib.parse import urlencode

from pyppeteer import launch


class HttpError(Exception):
    def __init__(self, response, body):
        self.response = response
        self.body = body

class BrowserRequests:
    
    @classmethod
    async def request(cls, url, req: dict):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.setRequestInterception(True)
        async def intercept(request):
            headers = {
                **req['headers'],
                'User-Agent': 'Zaap 3.12.2',
                'accept': '*/*',
                'accept-encoding': 'gzip,deflate'
            }
            newreq = {'headers': headers, 'method': req['method']}
            if req["method"] == "POST":
                post_data = urlencode(req['data']) if req['data'] else None
                newreq['postData'] = post_data
            await request.continue_(newreq)
        page.on('request', lambda req: asyncio.ensure_future(intercept(req)))
        # print("[HTTP] request", req.get('method'), url)
        response = await page.goto(url)
        text_response = await response.text()
        # print("[HTTP] result", req.get('method'), url, response.status, text_response)
        json_content = (204 != response.status) and 'content-type' in response.headers and 'application/json' in response.headers.get('content-type')
        if json_content:
            text_response = json.loads(text_response)
        await browser.close()
        if response.status >= 400:
            raise HttpError(response, text_response)
        return {'body': text_response}
    
    @classmethod
    async def post(cls, url, data, headers={}):
        return await cls.request(url, {
            "method": "POST",
            "data": data,
            "headers": headers,
        })
    
    @classmethod
    async def get(cls, url, headers = {}):
        return await cls.request(url, {
            "method": "GET",
            "headers": headers
        })