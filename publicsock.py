import config
import numpy as np
import analysis
async def onmessage(data,queue):
    if 'event' in data:
        print(data['event'])
        if data['event']=='unsubscribe':
            instid=data['arg']['instId']
            if config.strategies[instid]:
                del config.strategies[data['arg']['instId']]
    elif 'data' in data:
        channel = data['arg']["channel"]
        instid = data['arg']['instId']
        timeflag = channel + "_timeflag"
        obj = config.strategies[instid]
        for item in data['data']:
            # t,o,h,l,c,n,_=item
            if obj[timeflag] != item[0]:
                obj[timeflag] = item[0]
                obj[channel][0] = item
                obj[channel] = np.roll(obj[channel], -1, axis=0)
            else:
                obj[channel][99] = item
        await position.checkstop(instid, item[4])
        await analysis.main(instid)

async def onconnect(queue):
    pass
from positionandorder import position