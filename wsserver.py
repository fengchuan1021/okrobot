import asyncio
import websockets
import json
socks=[]
async def handler(websocket):
    socks.append(websocket)
    while True:
        try:
            message = await websocket.recv()
            if message=='ping':
                await websocket.send('pong')
                continue
            print(message)
            await websocket.send(json.dumps({"hello": message}))
        except Exception as e:
            socks.remove(websocket)
            break
async def send(msg):

    for sock in socks:

        await sock.send(msg)
async def main():
    async with websockets.serve(handler, "", 9999):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
    # loop=asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.create_task(websockets.serve(handler, "", 9999))
    # loop.run_until_complete(asyncio.sleep(300000))