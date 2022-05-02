import aioredis
DEBUG=1
delttime=0
pubsocketurl="wss://ws.okx.com:8443/ws/v5/public"
prisocketurl="wss://ws.okx.com:8443/ws/v5/public"
apikey="086d1a76-a86e-4e76-acbd-8236533f0a0c"
secret="EB5E9C07D55AB581681F39E8181F324A"
restserver='https://aws.okx.com'
redis = aioredis.Redis.from_url(
    'redis://:Xiaochuan1021@r-bp1s5xd87z4k1g5021pd.redis.rds.aliyuncs.com:6379/6?encoding=utf8')
if DEBUG:
    pubsocketurl="wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
    prisocketurl = "wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999"
    apikey="bd84331d-098a-4f64-8961-5f6acec48239"
    secret="D9A1F0D04D250D7BCE61428D79745933"
    restserver = "https://www.ouyicn.photo"
    redis = aioredis.Redis.from_url(
        'redis://:Xiaochuan1021@r-bp1s5xd87z4k1g5021pd.redis.rds.aliyuncs.com:6379/8?encoding=utf8')

strategies={}