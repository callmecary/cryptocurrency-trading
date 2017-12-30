import asyncio, websockets

@asyncio.coroutine
def hello():
    websocket = yield from websockets.connect('wss://ws-feed.gdax.com')
    try:
        greeting = yield from websocket.recv()
        print("< {}".format(greeting))

    finally:
        yield from websocket.close()

asyncio.get_event_loop().run_until_complete(hello())

"""
ws = websocket.WebSocket()
#ws.connect("wss://ws-feed.gdax.com")

send_string = json.loads('{"type": "subscribe", "product_ids": ["BTC-USD"], "channels": '
                         '["level2", "heartbeat", {"name": "ticker","product_ids": ["BTC-USD"]},]}')

print send_string
#ws.send(send_string)
print("Sent")
print("Receiving...")
#result = ws.recv()
print("Received '%s'" % result)
#ws.close()
"""
