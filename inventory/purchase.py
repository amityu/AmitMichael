#!/usr/bin/env python
# coding: utf-8

# In[1]:

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
plt.interactive(False)
import seaborn as sns
import numpy as np
import pandas as pd
from scipy.optimize import root_scalar
from scipy.stats import binom
from datetime import date
from tqdm import tqdm
import os
from sklearn.metrics import mean_squared_error
print (os.getcwd())
import itertools
import math

#   --------------------------- parameters and data --------------
PATH = '../resources/inventory/'
security_levels = np.linspace(0.90,0.99,5).tolist()
forecast_lengths = np.linspace(120, 180, 3).tolist()   #how many days to forcast, must start with zero
security_levels = [0.94]
forecast_lengths = [145]   #how many days to forcast, must start with zero
forecast_borders = [0] +  forecast_lengths +[10000]
supplier_list = [200067]  #200067 -julia
df = pd.read_csv(PATH + 'pl1020-1022.csv') #ניהול מלאי\דוחות\משלוח סחורה ללקוחות
purchase_data_df = pd.read_csv(PATH + 'purchase_pn_data.csv')#  נתוני רכש למוצר
avail_df = pd.read_csv(PATH + 'product_availability.csv')#דוח זמינות מוצרים
start_date = '07/12/21'  # all information retrieved from the ERP# software will be discarded. format 'dd\mm\yy'
start_date = start_date.split('/')[0] + '/' + start_date.split('/')[1] + '/' + start_date.split('/')[2]  # changing order


#heb_mon = [ "ינו","פבר","מרץ","אפר","מאי","יונ","יול","אוג","ספט","אוק","נוב","דצמ"]


# In[2]:

def preprocessing(df,avail_df,purchase_data_df,start_date):
    purchase_data_df = purchase_data_df.rename(columns={'מק"ט': 'pn', 'מלאי בטחון': 'security_stock', 'ספק מועדף': 'prefered_supplier'})

    avail_df = avail_df.rename(columns={"מק'ט": 'pn', 'כמות': 'avail_qty'})
    avail_df = avail_df.groupby(['pn']).agg({'avail_qty': 'sum'}).reset_index()

    format='%d/%m/%Y'
    df =df.rename(columns={"מק'ט": 'pn', 'כמות':'qty'})
    df = df.merge(purchase_data_df[['pn', 'prefered_supplier','security_stock']], 'left', on='pn')
    #df = df[df['prefered_supplier']== supplier]
    df['date'] = pd.to_datetime(df['תאריך.1'], format=format)
    df = df[df['date']>start_date]
    df['count'] = df['qty'].copy()
    min_date = df['date'].min()
    max_date = df['date'].max()
    days_no =(max_date-min_date).days
    print ('min date %s max date %s total %d days'%(min_date,max_date, days_no))


    # In[3]:




    # In[4]:


    #plots histogram of items per mean number of days between 2 orders
    #'count' number of orders
    #'qty' sum of item ordered

    df = df.groupby(['pn','prefered_supplier']).agg({'count':'count', 'qty': 'sum','security_stock':'mean'}).reset_index()

    df['p'] = df['count'].apply (lambda x:x/days_no)
    df['days_to_order']= df['p'].apply(lambda x: 1/x)
    #plt.figure()
    #sns.histplot(data=df, x = 'days_to_order')
    #plt.show()

    # In[5]:


    df = df[df['count'] != 0]
    df['mean_order'] = df['qty']/df['count']
    #forecast_period_length = 180
    #mean_order =100
    return df[['pn','p','days_to_order','mean_order','security_stock','prefered_supplier']],avail_df,purchase_data_df

def stock_level_per_security_level(p, mean_order, security_level, forecast_period_length):
    ''' this function finds the root of function f which finds the probability of a stock level for specific time'''

    def f(stock_level):
        return security_level - (
                    1 - binom.cdf(forecast_period_length - int(stock_level / mean_order), forecast_period_length,
                                  1 - p))

    return root_scalar(f, bracket=[0,forecast_period_length * mean_order]).root

    # In[6]:



    #days_to_order_range = forecast_lengths.tolist()


    # In[7]:


df,avail_df,purchase_data_df = preprocessing(df,avail_df,purchase_data_df,start_date)
'''

calculates stock reccomend dataframe
for each days length and security level recomend stock'''
def stock_recomend(df):
    security_series =[]
    result_dict = {'pn':[], 'days_to_order':[],'security':[],'forecast':[], 'stock_recomendation':[]}
    for t, row in tqdm(df.iterrows()):
        p = row['p']
        mean_order = row['mean_order']
        result = {}

        for s in security_levels:
            for forecast in forecast_lengths:

                result_dict['pn'].append(row['pn'])
                #result_dict['p'].append(p)
                result_dict['days_to_order'].append(1/p)

                #result_dict['mean_order'].append(mean_order)

                result_dict['security'].append(s)
                result_dict['forecast'].append(forecast)
                result_dict['stock_recomendation'].append(stock_level_per_security_level(p,mean_order,s,forecast))

        security_series.append(result)


    stock_recomend_df = pd.DataFrame.from_dict(result_dict)
    stock_recomend_df.to_csv(PATH+'recomend.csv')
    return stock_recomend_df

# In[7]:

stock_recomend_df = stock_recomend(df)
#stock_recomend_df = pd.read_csv(PATH+'recomend.csv')
df = df.merge(stock_recomend_df, on = ['pn','days_to_order'], how ='left')
df['error'] = (df['stock_recomendation'] - df['security_stock'])**2
# In[8]:
print()



#final_df = df.merge(purchase_data_df[['pn', 'security_stock','prefered_supplier']],'left',on='pn')

#computes dataframe with the diffrences between the stock recommendation to the current

'''
def calculate_error_from_limor(df):
    # security stock of product with frequenct p in the specific security level and days

    #mse_df = mse_df.merge(p_final_df,'inner',on ='pn')
    error = []
    for idx, row in df.iterrows():
        error.append((row['stock_recomend'] - row
    if mse_df.size == 0:
        return 0
    compare_df = mse_df[['pn','stock_recomendation','security_stock']]
    error = math.sqrt(mean_squared_error(mse_df['stock_recomendation'], mse_df['security_stock']))
    print('daystoorder_pn %d forecast=%d security=%.2f error = %.2f' %(d,days,security,error))
    return df, mean_squared_error

answers = []
'''
def frequency_group(df):
    f_group_list = []
    for idx, row in df.iterrows():
        for f_g in range(len(forecast_borders) - 1):
            if  (forecast_borders[f_g] <= row['days_to_order']) & (
                    row['days_to_order'] < forecast_borders[f_g + 1]):
                f_group_list.append(f_g)
    df['frequency_group'] = f_group_list
    return df
df = frequency_group(df)


def calibrating(df):
    best_forecast_index = pd.Series(np.zeros(len(df.index), dtype=bool))
    calibrating_df = df.groupby(by = ['frequency_group','forecast','security'],as_index = False).mean()
    for f_g in calibrating_df['frequency_group'].values:
        f_g_calibrating_df = calibrating_df[calibrating_df['frequency_group']==f_g]
        indx =f_g_calibrating_df ['error'].argmin()
        best_security = f_g_calibrating_df.iloc[indx]['security']
        best_forecast = f_g_calibrating_df.iloc[indx]['forecast']

        best_forecast_index = best_forecast_index | ((df['frequency_group']== f_g )&
                                    (df['security'] == best_security) &
                                    (df['forecast'] == best_forecast))
    return  df[best_forecast_index]

# In[9]:
df = calibrating(df)




# In[10]:
'''



# In[19]:
for index,row in best_parameters.iterrows():
      tmp_stock = stock_recomend[(stock_recomend['security']==row['security']) & (stock_recomend['forecast'] == row['days forecast'])]

stock_recomend()
order_df = pd.DataFrame()
days_length_plus_zero = [0] + forecast_lengths
#for d in range(0, len(days_length_plus_zero)-1):

for index,row in best_parameters.iterrows():
    #build p_final_df as final_df of specific days to order group with the selected supplier
    p_final_df =final_df[(days_length_plus_zero[d]<=final_df['days_to_order']) & (final_df['days_to_order']<days_length_plus_zero[d+1])].copy()[['pn','days_to_order','prefered_supplier']]

    p_final_df = p_final_df.loc[p_final_df['prefered_supplier'] ==supplier]

    if p_final_df.size ==0:
            continue
    p_stock_recommend = stock_recomend.copy()
    if d not in best_parameters['days_to_order']:
        continue
    recommnded_security_for_this_group = best_parameters[best_parameters['days_to_order']==d]['security'].values[0]

    p_stock_recommend = p_stock_recommend [p_stock_recommend['security'] == recommnded_security_for_this_group]


    p_stock_recomend = p_stock_recommend[p_stock_recommend['forcast'] == forecast_lengths[d]]

    #to_merge = stock_recomend.loc[(stock_recomend['forcast']==best_parameters.iloc[d]['days forcast']) &(stock_recomend['security'] == best_parameters.iloc[d]['security'])]
    #to_append = p_final_df.merge(to_merge,'left', on ='pn')
    to_append = p_final_df.merge(p_stock_recomend,'inner', on ='pn')
    order_df = order_df.append(to_append)


order_df =order_df.merge(avail_df, 'left', on='pn')
order_df = order_df[order_df['stock_recomendation']>order_df['avail_qty']]
order_df['qty_to_order'] = order_df.apply(lambda row:row['stock_recomendation']-row['avail_qty'], axis =1)

order_df[['pn', 'qty_to_order']].to_csv(PATH + 'order.csv')
'''
df =df.merge(avail_df, 'left', on='pn')

order = df[df['stock_recomendation']>df['avail_qty']].copy()
order['qty_to_order'] =order['stock_recomendation']- order['avail_qty']
for supplier in supplier_list:
    supplier_order = order[order['prefered_supplier'] == supplier]
    supplier_order.to_csv(PATH + 'Julia_%d_order.csv'%int(supplier))
