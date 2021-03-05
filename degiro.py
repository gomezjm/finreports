import degiroapi
from degiroapi.product import Product
from degiroapi.order import Order
from degiroapi.utils import pretty_json
from datetime import datetime, timedelta, timezone
import numpy as np 
import pandas as pd
import krakenex

# DEGIRO--------
try:
    creds = pd.read_csv('./cred.csv')
    print("Credenciales cargadas correctamente")
except Exception as e:
    print("Imposible leer archivo ./cred.csv")
    print(e)

degiro = degiroapi.DeGiro()
degiro.login(creds.columns[0],creds.columns[1])
today = datetime.today()
#generar la tabla con el valor del portafolio del dia
portfolio = degiro.getdata(degiroapi.Data.Type.PORTFOLIO, True)
summary=[]

for x in portfolio:
    name = degiro.product_info(x['id'])["name"]
    if name[-3:] == 'ETF':
        ptype = 'ETF'
    elif x['positionType'] == 'CASH':
        ptype = 'CASH'
    else:
        ptype = 'STOCK'
    value = x['value']
    size = x['size']
    summary+=[[today.strftime("%d/%m/%y"),name,ptype,size,value]]

portfolio_df = pd.DataFrame(np.array(summary), columns=['date','stock','type','units','value'])

#generar la tabla con el historico de transacciones
transactions = degiro.transactions(datetime(2019, 1, 1), datetime.now())
summary=[]

for x in transactions:
    name = degiro.product_info(x['productId'])["name"]
    if x['buysell'] == 'B':
        ptype = 'BUY'
    else:
        ptype = 'SELL'
    size = x['quantity']
    value = x['totalPlusFeeInBaseCurrency']*-1
    dateutc = datetime.fromisoformat(x['date'])
    dateloc = dateutc.replace(tzinfo=timezone.utc).astimezone(tz=None)
    if value != 0:
        summary+=[[dateloc.strftime("%d/%m/%y"),name,ptype,size,value]]

transactions_df = pd.DataFrame(np.array(summary), columns=['date','stock','type','units','value'])

de_output = pd.concat([portfolio_df,transactions_df],axis=0)


#KRAKEN---------------
#configure api
k = krakenex.API()
try:
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

    finreport = pd.concat([de_output,kr_output],axis=0)
    filename = './files/finreport' + today.strftime("%y%m%d%H%M") + '.csv'
    finreport.to_csv(filename,index=False)
    print(finreport)
except Exception as e:
    print("No existe kraken.key")
    print(e)
    filename = './files/finreport' + today.strftime("%y%m%d%H%M") + '.csv'
    de_output.to_csv(filename,index=False)
    print(de_output)