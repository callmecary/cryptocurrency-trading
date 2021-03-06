""" GDAX market data connection """
import json
import base64
import hmac
import hashlib
import time
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException


class MarketData(object):
    """ market data class contain all low level market connectivity functions """

    def __init__(self, url="wss://ws-feed.gdax.com", products=None, auth=False,
                 api_key="", api_secret="", api_passphrase="", channels=None):
        if url.endswith("/"):
            self.url = url[:-1]
        self.products = products
        self.channels = channels
        self.stop = False
        self.error = None
        self.web_socket = None
        self.auth = auth
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.msg_count = 0
        self.channel_subscribers = {channel: dict()
                                    for channel in channels}

    def init(self, url='', products=None, auth=False, api_key='',
             api_secret='', api_passphrase='', channels=None):
        """ reinitialize the data field, please don't call this if 
            if you are not sure what you are doing
        """
        if url.endswith("/"):
            self.url = url[:-1]
        self.products = products
        self.channels = channels
        self.stop = False
        self.error = None
        self.web_socket = None
        self.auth = auth
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.msg_count = 0
        self.channel_subscribers = {channel: dict()
                                    for channel in channels}

    def get_channel_subscribers(self, channel):
        """ get the list of subscribers of this channel """
        return self.channel_subscribers[channel]

    def register(self, client, channel, callback=None):
        """ register client to subscribers list, if callback is None, will call on_message
            otherwise, call provided callback function
                current available channels:
                'ticker'
                'heartbeat'
                'level2'
                'full'
        """
        if callback is None:
            callback = getattr(client, 'on_message')
        self.get_channel_subscribers(channel)[client] = callback

    def unregister(self, client, channel):
        """ remove client from subscribers list """
        del self.get_channel_subscribers(channel)[client]

    def start(self):
        def _go():
            self._connect()
            self._listen()
            self._disconnect()

        self.stop = False
        self.thread = Thread(target=_go)
        self.thread.start()

    def _connect(self):
        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        if self.channels is None:
            sub_params = {'type': 'subscribe', 'product_ids': self.products}
        else:
            sub_params = {'type': 'subscribe',
                          'product_ids': self.products, 'channels': self.channels}

        if self.auth:
            timestamp = str(time.time())
            message = timestamp + 'GET' + '/users/self/verify'
            message = message.encode('ascii')
            hmac_key = base64.b64decode(self.api_secret)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(
                signature.digest()).decode('utf-8')

            sub_params['signature'] = signature_b64
            sub_params['key'] = self.api_key
            sub_params['passphrase'] = self.api_passphrase
            sub_params['timestamp'] = timestamp

        self.web_socket = create_connection(self.url)
        self.web_socket.send(json.dumps(sub_params))

        if self.type == "heartbeat":
            sub_params = {"type": "heartbeat", "on": True}
        else:
            sub_params = {"type": "heartbeat", "on": False}
        self.web_socket.send(json.dumps(sub_params))
        print("\n-- Socket Opened --")

    def _listen(self):
        while not self.stop:
            try:
                if int(time.time() % 30) == 0:
                    # Set a 30 second ping to keep connection alive
                    self.web_socket.ping("keepalive")
                data = self.web_socket.recv()
                msg = json.loads(data)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)
            else:
                self.on_message(msg)

    def _disconnect(self):
        if self.type == "heartbeat":
            self.web_socket.send(json.dumps(
                {"type": "heartbeat", "on": False}))
        try:
            if self.web_socket:
                self.web_socket.close()
        except WebSocketConnectionClosedException as e:
            pass
        self.on_close()

    def close(self):
        self.stop = True
        self.thread.join()

    def on_close(self):
        print("\n-- Socket Closed --")

    def on_message(self, msg):
        for subscriber, callback in self.subscribers.items():
            callback(msg)
        if msg['type'] == 'ticker':
            print(msg)
        self.msg_count += 1

    def on_error(self, e, data=None):
        self.error = e
        self.stop = True
        print('{} - data: {}'.format(e, data))
