import config
import time
import hmac
import base64
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
    elif 'arg' in data:
        channel=data['arg']['channel']
        if channel=='positions':
            pass
        elif channel=="orders":
            pass
        elif channel == "balance_and_position":
            pass


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
