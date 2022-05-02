import config
async def onmessage(data,queue):
    if 'event' in data:
        print(data['event'])
        if data['event']=='unsubscribe':
            del config.strategies['instid']
async def onconnect(queue):
    pass