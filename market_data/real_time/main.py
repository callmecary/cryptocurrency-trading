# FOMO
import time
import json
import os
import requests
import sys
from gdax_account import CoinbaseExchangeAuth
from client_socket import ClientSocket


def testAccount(production):
    api_account_url = production['api_url']
    auth = CoinbaseExchangeAuth(api_key=production['api_key'],
                                api_secret=production['api_secret'],
                                api_passphrase=production['api_pass'])
    # Get accounts
    r = requests.get(api_account_url + 'accounts', auth=auth)
    print(r.json())


def testMarketData(production):
    p_ids = ['BTC-USD']
    ws = ClientSocket(products=p_ids, auth=True,
                      api_key=production['api_key'],
                      api_secret=production['api_secret'],
                      api_passphrase=production['api_pass'],
                      channels=[
                          "level2",
                          "heartbeat",
                          {"name": "ticker",
                           "product_ids": p_ids}
                      ])
    ws.start()
    print(ws.url, ws.products)

    try:
        while True:
            print("\nMessageCount =", "%i \n" % ws.msg_count)
            time.sleep(1)
    except KeyboardInterrupt:
        ws.close()

    if ws.error:
        sys.exit(1)
    else:
        sys.exit(0)


def main(argv):
    pwd = os.getcwd()
    pwd = pwd + '/client_secrets.json'
    with open(pwd) as json_file:
        account = json.load(json_file)
        production = account['production']

    testAccount(production)
    testMarketData(production)

    print('=======PROGRAM STOP============')

if __name__ == '__main__':
    main(sys.argv[1:])
