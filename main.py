import asyncio
import os

from  wssocket import Wssocket
import privatesock
import publicsock
import config
from aiohttp import web
import json
import aiohttp
import request as myrequst
import numpy as np
loop =  asyncio.new_event_loop()
asyncio.set_event_loop(loop)
pubsock=None
prisock=None
loop.run_until_complete(myrequst.getdelttime())

pubsock=Wssocket(config.pubsocketurl)
prisock=Wssocket(config.prisocketurl)

async def _gethistorydata(instid):
    config.strategies[instid].update({"candle15m": np.zeros((100, 7), np.float32),
                                      "candle1D": np.zeros((100, 7), np.float32),
                                      "candle15m_timeflag": 0,
                                      "candle1D_timeflag": 0,
                                      })

    async with aiohttp.ClientSession() as session:
        async with session.get(config.restserver + f'/api/v5/market/candles?instId={instid}&bar=15m') as r:
            data = await r.json()
            tmp = data['data'][::-1]
            config.strategies[instid]['candle15m'] = tmp
            print('timeflag', tmp[-1][0])
            config.strategies[instid]['candle15m_timeflag'] = tmp[-1][0]
            # print(config.hooks[instid]['candle15m'])
        async with session.get(config.restserver + f'/api/v5/market/candles?instId={instid}&bar=1D') as r:
            data = await r.json()
            tmp = data['data'][::-1]
            config.strategies[instid]['candle1D'] = tmp
            print('timeflag', tmp[-1][0])
            config.strategies[instid]['candle1D_timeflag'] = tmp[-1][0]
            # print(config.hooks[instid]['candle1day'])

    await pubsock.sendqueue.put({
                    "op": "subscribe",
                    "args": [{
                        "channel": "candle15m",
                        "instId": instid
                    },
                        {
                            "channel": "candle1D",
                            "instId": instid
                        }
                    ]
                })
async def addstrategy(request):
    strategy= await request.json()
    print('stra',strategy)
    instid=strategy['instid']
    await config.redis.hset('strategies',strategy['instid'],await request.read())

    if instid not in config.strategies:
        config.strategies[instid]={}
        await _gethistorydata(instid)
    config.strategies[instid]['strategy']=strategy
    return web.Response(text='done')
async def getstrategies(request):
    return web.json_response({'status':0,'data':{instid:config.strategies[instid]['strategy'] for instid in config.strategies}})
async def getallswapproducts(request):
    return web.json_response({'status':0,'data':await myrequst.getallswapproducts()})
async def delstratogy(request):
    instid = request.rel_url.query['instid']
    await config.redis.hdel('strategies', instid)
    await pubsock.sendqueue.put({
                    "op": "unsubscribe",
                    "args": [{
                        "channel": "candle15m",
                        "instId": instid
                    },
                        {
                            "channel": "candle1D",
                            "instId": instid
                        }
                    ]
                })

    web.json_response({'status':0})

async def initstrategies():

    val = await config.redis.hgetall('strategies')
    print('val',val)
    for instid in val:
        config.strategies[instid.decode()]={'strategy':json.loads(val[instid])}

    th=[_gethistorydata(i.decode()) for i in val]
    if th:
        await asyncio.gather(*th)
loop.run_until_complete(initstrategies())


loop.create_task(pubsock.init(loop,publicsock.onmessage,publicsock.onconnect))
loop.create_task(prisock.init(loop, privatesock.onmessage, privatesock.onconnect))
app = web.Application()
app.add_routes([web.post('/addstrategy', addstrategy),
                web.get('/getstrategies',getstrategies),
                web.get('/getallswapproducts',getallswapproducts),
                web.get('/delstratogy',delstratogy),


                ])

web.run_app(app, loop=loop)

