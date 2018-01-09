# FOMO
import time
import json
import os
import requests
import sys
from account import Account
from gdax_account import CoinbaseExchangeAuth
from gdax_connect import ClientSocket


def testAccount():
    api_account_url = 'https://api.gdax.com/'
    account = Account()
    auth = CoinbaseExchangeAuth(account.API_KEY,
                                account.API_SECRET,
                                account.API_PASS)
    # Get accounts
    r = requests.get(api_account_url + 'accounts', auth=auth)
    print(r.json())


def testMarketData():
    account = Account()
    p_ids = ['BTC-USD']
    ws = ClientSocket(products=p_ids, auth=True, api_key=account.API_KEY,
                      api_secret=account.API_SECRET, api_passphrase=account.API_PASS,
                      channels=["heartbeat",
                                {"name": "ticker",
                                 "product_ids": p_ids}])
    ws.start()
    print(ws.url, ws.products)

    try:
        while True:
            print("\nMessageCount =", "%i \n" % ws.msg_count)
            time.sleep(1)
    except KeyboardInterrupt:
        ws.close()


def main(argv):
    testAccount()
    testMarketData()
    print('=======PROGRAM STOP============')
    if ws.error:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
