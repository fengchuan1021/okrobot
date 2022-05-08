import math
import os

import config
import request as myrequest
import time
from collections import defaultdict
class PositionandOrder:
    def __init__(self):
        self.positions =defaultdict(lambda:{'short':{},'long':{}})
        self.orders=defaultdict(lambda:{'short':{},'long':{},'sl':defaultdict(dict),'bs':defaultdict(dict)})
        self.autoid=0
        self.mycash=0

    async def gethistoryorder(self,loop):
        data=await myrequest.gethistoryorder()
        tmpsl =defaultdict(dict)
        tmpbs =defaultdict(dict)

        tmpdirect={}
        tmpinstids={}
        for order in data:

            if not order['clOrdId']:
                continue
            tmpzo = await config.redis.hget('lastzotime', f"{order['instId']}{order['posSide']}")
            tmpzo = 0 if not tmpzo else int(tmpzo)

            if self.positions[order['instId']][order['posSide']]!='0':

                if order['clOrdId'].startswith('bl') and int(order['uTime'])>tmpzo:
                    tmpdirect[order['clOrdId']]='long'
                    tmpinstids[order['clOrdId']]=order['instId']
                    self.orders[order['instId']]['long'][order['clOrdId']]=order
                elif order['clOrdId'].startswith('ss') and int(order['uTime'])>tmpzo:
                    tmpdirect[order['clOrdId']] = 'short'
                    tmpinstids[order['clOrdId']] = order['instId']
                    self.orders[order['instId']]['short'][order['clOrdId']]=order

            if order['clOrdId'].startswith('sl')  and int(order['uTime'])>tmpzo:
                originorderid = order['clOrdId'].replace('sl', 'bl')[0:-2]
                tmpsl[originorderid][order['clOrdId']]=order
            elif order['clOrdId'].startswith('bs')  and int(order['uTime'])>tmpzo:
                originorderid = order['clOrdId'].replace('sl', 'bl')[0:-2]
                tmpbs[originorderid][order['clOrdId']]=order
        for originorderid in tmpsl:
            if originorderid in tmpdirect:
                s=0
                for orderid in tmpsl[originorderid]:
                    order=tmpsl[originorderid][orderid]
                    s+=int(order['accFillSz'])
                instid=tmpinstids[originorderid]
                if s==int(self.orders[instid]['long'][originorderid]['accFillSz']):
                    del self.orders[instid]['long'][originorderid]
                else:
                    self.orders[instid]['sl'][orderid]=tmpsl

        for originorderid in tmpbs:
            if originorderid in tmpdirect:
                s=0
                for orderid in tmpbs[originorderid]:
                    order = tmpsl[originorderid][orderid]
                    s+=int(order['accFillSz'])
                instid = tmpinstids[originorderid]
                if s==int(self.orders[instid]['short'][originorderid]['accFillSz']):
                    del self.orders[instid]['short'][originorderid]
                else:
                    self.orders[instid]['bs'][orderid]=tmpbs

    async def _checkstop(self,order,price,direction):

        newprice=float(price)
        oldprice=float(order['px'])

        rat=(newprice-oldprice)/oldprice*3*direction
        stopstrategy=None
        if rat<0:
            stopstrategy=config.strategies[order['instId']]['strategy']['stoploss']
        else:
            if 'mxrat' not in order:
                order['mxrat']=rat
                return
            else:
                if rat>=order['mxrat']:
                    order['mxrat']=rat
                    return
                else:
                    rat=(rat-order['mxrat'])/order['mxrat']
                    stopstrategy = config.strategies[order['instId']]['strategy']['stopwin']
        diff=abs(rat)*100
        sellsz=0
        hassell=0
        for item in stopstrategy:
            if(diff>=item['withdrawal']):

                sellsz=math.ceil(item['percent']*int(order['accFillSz'])/100)
                d='sl' if direction==1 else 'bs'
                for tmporderid in self.orders[order['instId']][d][order['clOrdId']]:
                    tmporder=self.orders[order['instId']][d][order['clOrdId']][tmporderid]
                    hassell+=int(tmporder['accFillSz'])
                break
        left=int(order['accFillSz'])-hassell
        sellsz=sellsz if sellsz<left else left
        if sellsz>0:
            d = 'sl' if direction == 1 else 'bs'
            if direction==1:
                traceid=order['clOrdId'].replace('bl','sl')+'{:0>2}'.format(len(self.orders[order['instId']][d][order['clOrdId']]))
            else:
                traceid=order['clOrdId'].replace('ss','bs')+'{:0>2}'.format(len(self.orders[order['instId']][d][order['clOrdId']]))
            await self.order(order['instId'],'sell' if direction==1 else 'buy','long' if direction==1 else 'short',price,sellsz,traceid)

    async def checkstop(self,instid,newprice):

        for orderid in self.orders[instid]['short']:

            await self._checkstop(self.orders[instid]['short'][orderid],newprice,-1)
        for orderid in self.orders[instid]['long']:
            await self._checkstop(self.orders[instid]['long'][orderid],newprice,1)
    async def setpositions(self,data):
        for p in data:
            if p['pos']=='0':
                self.positions[p["instId"]][p['posSide']]={}
                tmp='bs' if p['posSide']=='short' else 'sl'
                self.orders[p["instId"]][tmp]=defaultdict(dict)
                await config.redis.hset("lastzotime",p["instId"]+p['posSide'],int(time.time()*1000))
            self.positions[p["instId"]][p['posSide']]=p
    async def getpositons(self):
        data=await myrequest.getpositions()
        await self.setpositions(data)
    async def init(self,loop,pubsock,prisock):
        self.pubsock = pubsock
        self.prisock =prisock
        await self.getpositons()
        print(self.orders)

        await self.gethistoryorder(loop)
        data=await myrequest.getbalance()
        for item in data:
            print(item)
            if item['details'][0]['ccy']=='USDT':
                self.mycash=float(item['details'][0]['cashBal'])
                break
    async def order(self,instid,side,posside,price,number,traceid):
        self.autoid+=1
        print('order:',instid,side,posside,price,number,traceid)
        data={
            "id": self.autoid,
            "op": "order",
            "args": [{
                "side": side,
                "instId": instid,
                "tdMode": "isolated",
                "ordType": "limit",
                "posSide": posside,
                "px": str(price),
                "sz": str(number),
                "clOrdId":traceid
            }]
        }
        await self.prisock.sendqueue.put(data)
    async def buylong(self,instid,price):
        print('buylong')
        print(f'{self.mycash=}')
        print(f"{config.strategies[instid]['strategy']['positionrat']=}")
        print(f"{price=}")
        print(f"{config.strategies[instid]['strategy']['ctval']=}")
        n=int(self.mycash*config.strategies[instid]['strategy']['positionrat']/100/float(price)/float(config.strategies[instid]['strategy']['ctval']))
        #self.autoid+=1
        print('buy n',n)
        if n >0:
            traceid='bl'+str(int(time.time()*1000))
            await self.order(instid,'buy','long',price,n,traceid)
    async def sellshort(self,instid,price):
        print('sellshort')

        print(f'{self.mycash=}')
        print(f"{config.strategies[instid]['strategy']['positionrat']=}")
        print(f"{price=}")
        print(f"{config.strategies[instid]['strategy']['ctval']=}")
        n=int(self.mycash*config.strategies[instid]['strategy']['positionrat']/100/float(price)/float(config.strategies[instid]['strategy']['ctval']))
        #self.autoid+=1
        print('buy n',n)
        if n>0:
            traceid='ss'+str(int(time.time()*1000))
            await self.order(instid,'buy','long',price,n,traceid)
        #await self.order(instid,'sell','short',price)

position=PositionandOrder()
if __name__ == "__main__":
    import asyncio

    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    p=PositionandOrder()
    loop.run_until_complete(myrequest.getdelttime())
    loop.run_until_complete(p.init(loop))