import asyncio, websockets
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from account import Account

@asyncio.coroutine
def hello():
    websocket = yield from websockets.connect('wss://ws-feed.gdax.com')
    try:
        greeting = yield from websocket.recv()
        print("< {}".format(greeting))

    finally:
        yield from websocket.close()


# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method+request.path_url+(request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

def main():
    api_url = 'https://api.gdax.com/'
    account = Account()
    auth = CoinbaseExchangeAuth(account.API_KEY,
                                account.API_SECRET,
                                account.API_PASS)

    # Get accounts
    r = requests.get(api_url + 'accounts', auth=auth)
    print(r.json())
    #asyncio.get_event_loop().run_until_complete(hello())

if __name__ == '__main__':
    main()
