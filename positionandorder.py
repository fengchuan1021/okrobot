import request as myrequest
class PositionandOrder:
    def __init__(self):
        pass

    async def gethistoryorder(self,loop):
        data=await myrequest.gethistoryorder()
        print(data)
        pass

    async def init(self,loop):
        await self.gethistoryorder(loop)


if __name__ == "__main__":
    import asyncio

    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    p=PositionandOrder()
    loop.run_until_complete(myrequest.getdelttime())
    loop.run_until_complete(p.init(loop))