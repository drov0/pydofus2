import os 
from lxml import html
curdir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(curdir, "response_haapi.html")
response = open(file, "r").read()
root = html.fromstring(response)
error = root.xpath('//span[@class="error-description"]')[0].text
errorCode = root.xpath('//span[@class="code-label"]//span')[0].text

print("Login Token creation failed, reason: %s\nerror code %s" % (error, errorCode))
