""" main function system entry point"""
import time
import json
import os
import sys
import requests
from gdax_account import CoinbaseExchangeAuth
from client_socket import ClientSocket


def test_account(production):
    """client account information -> return client account information"""
    api_account_url = production['api_url']
    auth = CoinbaseExchangeAuth(api_key=production['api_key'],
                                api_secret=production['api_secret'],
                                api_passphrase=production['api_pass'])
    request_return = requests.get(api_account_url + 'accounts', auth=auth)
    print(request_return.json())


def test_marketdata(production):
    """client account information -> setup GDAX connection and print data"""
    p_ids = ['BTC-USD']
    client_socket = ClientSocket(products=p_ids, auth=True,
                                 api_key=production['api_key'],
                                 api_secret=production['api_secret'],
                                 api_passphrase=production['api_pass'],
                                 channels=[
                                     "level2",
                                     "heartbeat",
                                     {"name": "ticker",
                                      "product_ids": p_ids}
                                 ])
    client_socket.start()
    print(client_socket.url, client_socket.products)

    try:
        while True:
            print("\nMessageCount =", "%i \n" % client_socket.msg_count)
            time.sleep(1)
    except KeyboardInterrupt:
        client_socket.close()

    if client_socket.error:
        sys.exit(1)
    else:
        sys.exit(0)


def main(argv):
    """system entry point  argv  commandline arguments"""
    pwd = os.getcwd()
    pwd = pwd + '/client_secrets.json'
    with open(pwd) as json_file:
        account = json.load(json_file)
        production = account['production']
    test_account(production)
    test_marketdata(production)
    print('=======PROGRAM STOP============')

if __name__ == '__main__':
    main(sys.argv[1:])
