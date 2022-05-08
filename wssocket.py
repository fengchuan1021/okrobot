import asyncio

import websockets
import json
import time
class Wssocket:
    def __init__(self,endpoint):
        self.endpoint = endpoint
        self.lastrecv=0
        self.pongsingnal=None
        self.close = False
        self.callback=None
        self.sock=None
        self.sendqueue= asyncio.Queue()
    async def init(self,loop,onmessage,onconnect):
        self.loop = loop
        self.callback=onmessage
        while 1:
            if 1:
            #try:
                self.close=False
                self.sock=await websockets.connect(self.endpoint,ping_interval=None)
                await onconnect(self.sendqueue)
                print('crate sock ok?')
                t1=loop.create_task(self.ping())
                t2=loop.create_task(self.recv())
                s=loop.create_task(self.send())
                results=await asyncio.gather(t1,t2,s)
                print('results',results)
            # except Exception as e:
            #     t1.cancel()
            #     t2.cancel()
            #     s.cancel()
            #     print(e, 20)
            #     self.close=True

                await asyncio.sleep(0.1)
    async def ping(self):
        #print('self.sock',self.sock)
        print('self.close:',self.close)
        while not self.close:

            await asyncio.sleep(5)
            if time.time()-self.lastrecv>15:
                #print('send ping')
                await self.sock.send('ping')
                self.pongsingnal=self.loop.create_future()
                await asyncio.wait_for(self.pongsingnal,timeout=15)

    async def send(self):
        while not self.close:
            msg=await self.sendqueue.get()
            await self.sock.send(json.dumps(msg))

    async def recv(self):
        print('what a fuck?')
        while not self.close:

            self.lastrecv = time.time()
            data=await self.sock.recv()

            if data=='pong':
                self.pongsingnal.set_result(None)
                continue
            await self.callback(json.loads(data),self.sendqueue)





