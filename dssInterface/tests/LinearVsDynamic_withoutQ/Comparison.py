# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 09:38:21 2018

@author: guemruekcue
"""

from maxPV_linear  import maxPVLin
from minGrid_linear  import minGridLin
from minPBill_linear  import minPBillLin

#%%
from datetime import date, datetime, time, timedelta
the_time =  datetime.combine(date.today(), time(0, 0))
timestamp=[]

for t in range(1440):
    timestamp.append("{:02d}:{:02d}".format(the_time.hour,the_time.minute))
    the_time = the_time + timedelta(minutes=1)

import pandas
import matplotlib.pylab as plt

v_maxPV=maxPVLin['Voltage']
v_minPgrid=minGridLin['Voltage']
v_minPBill=minPBillLin['Voltage']

    
df_volt=pandas.DataFrame(list(zip(timestamp, v_maxPV,v_minPgrid,v_minPBill)),columns=['Time [h]','Maximize PV','Minimize Imp/Exp','Minimize Bill'])
fig1, ax1= plt.subplots(1, 1)
#df_volt.plot(x='Time',y=['Maximize PV','Minimize Imp/Exp','Minimize Bill'],rot=90, ax=ax1,legend=True)
df_volt.plot(x='Time [h]',y='Maximize PV',rot=90, ax=ax1,legend=True,linestyle='-')
df_volt.plot(x='Time [h]',y='Minimize Imp/Exp',rot=90, ax=ax1,legend=True,linestyle='--')
df_volt.plot(x='Time [h]',y='Minimize Bill',rot=90, ax=ax1,legend=True,linestyle='dotted')

ax1.set_title('Voltage R')
ax1.set_ylabel('p.u')
ax1.xet_ylabel('Time [h]')

fig1.savefig("Voltage.png")
