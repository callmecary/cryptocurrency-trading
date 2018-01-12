import json
import hmac
import hashlib
import time
import requests
import base64
from requests.auth import AuthBase

# Create custom authentication for Exchange


class CoinbaseExchangeAuth(AuthBase):

    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + \
            request.path_url + (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        })
        return request
