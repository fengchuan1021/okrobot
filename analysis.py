import numpy as np
import aiohttp
import time
import asyncio
from positionandorder import position

TIME=0
OPEN=1
HIGH=2
LOW=3
CLOSE=4
NUMBER=5
MONEY=6
import config

from collections import defaultdict
lastbuytime=defaultdict(int)
async def followpolicy(index):
    if 1:

        table=config.strategies[index]["candle15m"]
        if table[99][CLOSE]>table[98][CLOSE] and table[98][CLOSE]>table[97][CLOSE] and table[98][NUMBER]>table[97][NUMBER]:

            if time.time()-lastbuytime[index]>60:
                print("跟随策略凯多", index)
                lastbuytime[index] = time.time()
                await position.buylong(index,table[99][CLOSE])
                #await buy()
        elif table[99][CLOSE] < table[98][CLOSE] and table[98][CLOSE]< table[97][CLOSE] and table[98][NUMBER]>table[97][NUMBER]:

            if time.time()-lastbuytime[index]>60:
                print("跟随策略开空", index)
                lastbuytime[index] = time.time()
                await position.sellshort(index, table[99][CLOSE])
                #await sell()


# def presspolicy(instid):
#     #1小时压力线 #4小时压力线 #1天压力线
#     flag=[0,0,0]
#     maz=[0,0,0]
#     miz=[0,0,0]
#     for i,n in enumerate([5,21,99]):
#         data=table[index][99-n:99]
#         ma=data[:,1].max()
#         mi=data[:,2].min()
#         if table[index][99][CLOSE]<ma and (ma-table[index][99][CLOSE])/table[index][99][CLOSE]<=0.01:
#             flag[i]=-1
#             maz[i]=ma
#         if table[index][99][CLOSE]>mi and (table[index][99][CLOSE]-mi)/table[index][99][CLOSE]<=0.01:
#             flag[i]=1
#             miz[i]=mi
#     s=sum(flag)
#     if s==3:
#         if time.time()-presstime[index]>15*60:
#             presstime[index]=time.time()
#             buy(index,min(miz))
#     elif s==-3:
#         if time.time()-presstime[index]>15*60:
#             presstime[index]=time.time()
#             sell(index,max(maz))
#     elif s>=2:
#         if time.time()-presstime[index]>15*60:
#             presstime[index]=time.time()
#             buy(index, min(miz))
#     elif s==-2:
#         if time.time()-presstime[index]>15*60:
#             presstime[index]=time.time()
#             sell(index, max(maz))
#

async def main(instid):
    await followpolicy(instid)
    #await presspolicy(instid)
