from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar
import json
import datetime
from urllib.request import Request, urlopen

def handler(event, context):
    username = event['account']['username']
    password = event['account']['password']

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
        urllib.request.HTTPHandler())
    opener.addheaders = [('User-agent', "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36")]

    req = Request('https://www.bondora.com/en', headers={'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"})
    html = opener.open(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    csrf = soup.select('input[name="__RequestVerificationToken"]')[0]['value']
    postdata = urllib.parse.urlencode({"__RequestVerificationToken":csrf,
                                       "returnUrl":"/en",
                                       "Email":username,
                                       "Password":password}).encode("utf-8")

    req = Request('https://www.bondora.com/en/login',
                data=postdata,
                method='POST')

    response = opener.open(req)
    html = response.read()

    req = Request('https://www.bondora.com/en/dashboard/overviewnumbers/',
      headers={'User-Agent': "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36"},
      method='GET')

    html = opener.open(req).read()
    x = json.loads(html)
    balance = x['Stats'][0]['Value'].replace('€','').replace(',','')
    available = x['Stats'][4]['Value'].replace('€','').replace(',','')
    invested = x['Stats'][3]['Value'].replace('€','').replace(',','')

    result = {"balance":balance,"available":available,"invested":invested}
    resultStr = json.dumps(result)
    customcontext = context.client_context.custom
    if "lastvalue" in customcontext and resultStr == customcontext['lastvalue']:
      return
    else:
      result['dedupid']=resultStr
      return result
