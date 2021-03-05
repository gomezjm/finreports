import krakenex
from datetime import datetime
import numpy as np 
import pandas as pd
#configure api
k = krakenex.API()
k.load_key('./kraken.key')

open_positions = k.query_private('Ledgers')

order_hist = []

for x in open_positions['result']['ledger']:
    if open_positions['result']['ledger'][x]['type'] == 'spend':
        ptype = 'BUY'
        name = 'CRYPTO'
        date = datetime.fromtimestamp(open_positions['result']['ledger'][x]['time'])
        value = float(open_positions['result']['ledger'][x]['amount'])*-1
        for y in open_positions['result']['ledger']:
            if open_positions['result']['ledger'][y]['refid'] == open_positions['result']['ledger'][x]['refid'] and open_positions['result']['ledger'][y]['asset'] != 'EUR.HOLD':
                asset = open_positions['result']['ledger'][y]['asset']
                units = open_positions['result']['ledger'][y]['amount']
        order_hist+=[[date.strftime("%d/%m/%y"),asset,ptype,units,value]]

balance = k.query_private('Balance')
position = []
today = datetime.today()
date = today.strftime("%d/%m/%y")
currentvalue = k.query_public('Ticker', {'pair' : 'DOTEUR'})
for x in balance['result'].keys():
    stock = x
    units = balance['result'][x]
    value = float(units)*float(currentvalue['result']['DOTEUR']['p'][0])
    if float(units) > 0:
        position+=[[date,stock,'CRYPTO',units,value]]

order_hist_df = pd.DataFrame(np.array(order_hist), columns=['date','stock','type','units','value'])
position_df = pd.DataFrame(np.array(position), columns=['date','stock','type','units','value'])

kr_output = output = pd.concat([order_hist_df,position_df],axis=0)

print(kr_output)