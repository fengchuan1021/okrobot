import datetime
import hmac
import base64
import aiohttp
import config
import time

async def get(url):
    timestamp=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method="GET"
    requestpath=url
    sign=base64.b64encode(hmac.new(config.secret.encode(),(timestamp + 'GET' +url).encode(),digestmod='sha256').digest())
    headers = {"OK-ACCESS-KEY": config.apikey, 'OK-ACCESS-TIMESTAMP': timestamp,
               "OK-ACCESS-PASSPHRASE": "Xiaochuan1021@", "OK-ACCESS-SIGN": sign.decode(),
               "Content-Type": "application/json",
               "accept": 'application/json'
               }
    print('sign',sign.decode())
    if config.DEBUG:
        headers['x-simulated-trading'] = '1'
        async with aiohttp.ClientSession() as session:
            async with session.get(config.restserver+url,headers=headers) as r:
                data=await r.json()
                print(data)
                return data['data']

async def getallswapproducts():
    url = '/api/v5/public/instruments?instType=SWAP'
    return await get(url)
async def getdelttime():
    url="/api/v5/public/time"
    try:
        data=await get(url)
        #print('servertime:',int(data[0]['ts']))
        config.delttime=int(time.time())-int(int(data[0]['ts'])/1000)
        print('delttime',config.delttime)
    except Exception as e:
        print(e,37)
        pass

async def gethistoryorder():
    url='/api/v5/trade/orders-history?instType=SWAP'
    data=await get(url)
    print("len(data)",len(data))
    return data