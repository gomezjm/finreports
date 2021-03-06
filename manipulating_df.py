import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

date_to_filter = '05/03/21'
date = '20210305'
a = pd.read_csv('./csv/finreport210305.csv')
b = a[a['date'] == date_to_filter]
bb=b[['type','value']]
cc=pd.pivot_table(bb,values='value',index='type',aggfunc=np.sum,fill_value=0)
pieplot = cc.plot.pie(y='value',label='',autopct='%1.0f%%',labeldistance=1.2,figsize=(5, 5))
plt.title(f'Distribucion cartera - {date_to_filter}')
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol= 2)
plt.savefig(f'./plots/dist{date}.png')
barplot = cc.plot.bar(y='value',label='',rot=0,figsize=(5, 5))
plt.title(f'Valor cartera (€) - {date_to_filter}')
for index,value in enumerate(list(cc['value'])):
    plt.annotate(f'{str(int(value))}€',(index,value+50),ha='center',weight='bold')
plt.savefig(f'./plots/value{date}.png')


