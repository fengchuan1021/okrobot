import json

import config
import time
import hmac
import base64
import wsserver
from positionandorder import position
async def onmessage(data,queue):
    if 'event' in data:

        if data['event']=='login':
            tmp={
                        "op": "subscribe",
                        "args": [
                            {
                            "channel": "positions",
                            "instType": "SWAP",
                             },
                            {
                                "channel": "balance_and_position"
                            },
                            {
                                "channel": "orders",
                                "instType": "SWAP",

                            }
                            ]
            }
            await queue.put(tmp)
        else:
            print(data)
    elif 'arg' in data:

        channel=data['arg']['channel']
        if channel=='positions':
            print('positions:',data)
            await position.setpositions(data['data'])
            if wsserver.socks:
                await wsserver.send(json.dumps(data))
        elif channel=="orders":
            print('oderers:',data)
            order=data['data'][-1]
            instid=order['instId']
            clOrdId=order['clOrdId']
            side=order['side']
            posSide=order['posSide']
            if clOrdId:
                if (side=='buy' and posSide=='long') or (side=='sell' and posSide=='short'):
                    if clOrdId in position.orders[instid][order['posSide']]:
                        origin=position.orders[instid][order['posSide']][clOrdId]
                    position.orders[instid][order['posSide']][clOrdId]=order
                    if 'mxrat' in origin:
                        order['mxrat']=origin['mxrat']

                else:
                    pside='bs' if posSide=='short' else 'sl'
                    if posSide=='short':
                        pside = 'bs'
                        originorderid=clOrdId.replace('bs', 'ss')[0:-2]
                    else:
                        pside = 'sl'
                        originorderid = clOrdId.replace('sl', 'bl')[0:-2]
                    position.orders[instid][pside][originorderid][clOrdId] = order
        elif channel == "balance_and_position":
            for item in data['data'][0]['balData']:
                if item['ccy']=="USDT":
                    position.mycash=float(item['cashBal'])
                    break
        else:
            print(data)

async def onconnect(queue):
    timestamp=str(int(time.time())-config.delttime)
    sign = base64.b64encode(
        hmac.new(config.secret.encode(), (timestamp + 'GET' +'/users/self/verify').encode(), digestmod='sha256').digest())
    data={
            "op": "login",
            "args":
                [
                    {
                        "apiKey"    : config.apikey,
                        "passphrase" :"Xiaochuan1021@",
                        "timestamp" :timestamp,
                        "sign" :sign.decode()
                    }
                ]
        }
    await queue.put(data)
