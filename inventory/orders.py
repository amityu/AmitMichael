import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import date
PATH = 'resources/orders/'

# ------------ Histogram of orders enter oredrs
#df = pd.read_csv(PATH + 'shipment.csv')
#hist  = df.hist(column='total price', bins = range(1,20000,100),density=True,cumulative=True)
#plt.show()

# exponential grows of sales, enter פירוט חשבוניות חודשי change date to month and
# סכום ל sum

heb_mon = [ "ינו","פבר","מרץ","אפר","מאי","יונ","יול","אוג","ספט","אוק","נוב","דצמ"]


df = pd.read_csv(PATH + 'invoices.csv',encoding = "ISO-8859-8")
def to_date(x):
    s = x.split('-')
    return date(2000+int(s[1]), heb_mon.index(s[0])+1,28)
df['month'] = df['month'].apply(to_date)

df['month'] = pd.to_datetime(df['month'])
#calculate sum of values, grouped by quarter
df = df.groupby(['month'], as_index=False).sum()
#df.groupby(df['month'].dt.to_period('Q'))['sum'].sum()
df.plot.bar(x='month', y = 'sum')
fit = np.polyfit(np.arange(df.shape[0]), np.log(df['sum'].to_numpy()), 1)

#view the output of the model
# the sales is doing regression to exponential
print(" the fit parameter is should use exponent e^fit[1] * e^fit[0] **x")
print(fit)
e_fit = np.exp(fit)

print (" growth parameter of 1 year is " )
print( e_fit[0]**12)

x = np.arange(0, df.shape[0])
y = e_fit[1]*np.power(e_fit[0],x)
plt.plot(x,y)
plt.show()
