# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 11:47:42 2018

@author: guemruekcue
"""

from test_minGridExchange  import v11,v12,v13,SOCProfile1,PVUtil1
from test_maxPVUtilization import v21,v22,v23,SOCProfile2,PVUtil2
from test_minEleBill       import v31,v32,v33,SOCProfile3,PVUtil3,timestamp

import pandas
import os
import matplotlib.pyplot as plt
from Rainflow import *


#%%
os.chdir(r'C:\Users\guemruekcue\internship\optimization-agent\dssInterface\tests')
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(os.path.dirname(__file__), 'results/')
file_name="Comparison"



#%%
#Empirical parameters to determine rated cycle-life at different DoD ranges
#Example chosen such that 4000 clycle lifetime at 80% DoD 
A=2873.1
B=-1.483

#Rainflow counting: a list of tuples that contain load ranges and the corresponding number of cycles
rf1=count_cycles(SOCProfile1)
rf2=count_cycles(SOCProfile1)
rf3=count_cycles(SOCProfile1)

#Degradation of life-cycle
D_CL1=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf1)
D_CL2=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf1)
D_CL3=sum(pair[1]/(A*pow(pair[0],B)) for pair in rf1)

#PV Utilization
df_PV=pandas.DataFrame(list(zip(timestamp, PVUtil1, PVUtil2,PVUtil3)),
                        columns=['time','Model1','Model2','Model3'])

#SOC
df_SOC=pandas.DataFrame(list(zip(timestamp, SOCProfile1, SOCProfile2,SOCProfile3)),
                        columns=['time','Model1','Model2','Model3'])

#Phase voltage vectors
df_v1 = pandas.DataFrame(list(zip(timestamp, v11, v21,v31)), columns=['time','Model1','Model2','Model3'])
df_v2 = pandas.DataFrame(list(zip(timestamp, v11, v21,v31)), columns=['time','Model1','Model2','Model3'])
df_v3 = pandas.DataFrame(list(zip(timestamp, v11, v21,v31)), columns=['time','Model1','Model2','Model3'])

#%%
styles = ['r','g','b']
#ax1: Grid Exchange
#ax2: PVutilization
#ax3: Bill
#ax4: Battery degradation:SOC
#ax5: Voltage

#TODO: Measure the energy that PVNode bought and compare it in ax1
#TODO: Measure the electricity bill paid by PVNode and compare it in ax3

fig, (ax2,ax4,ax5) = plt.subplots(3, 1, sharex=True)
df_PV.plot(x='time',y=['Model1','Model2','Model3'],rot=90, style=styles, ax=ax2, legend=True)
df_SOC.plot(x='time',y=['Model1','Model2','Model3'],rot=90, style=styles, ax=ax4, legend=False)
df_v1.plot(x='time',y=['Model1','Model2','Model3'],rot=90, style=styles, ax=ax5, legend=False)

ax2.set_title('Pv Utilization', rotation='vertical',loc='right')
ax4.set_title('SOC', rotation='vertical',loc='right')
ax5.set_title('Voltage R', rotation='vertical',loc='right')


"""
plt.gcf().autofmt_xdate()
plt.ylabel('Voltage (p.u.)', fontsize=18)
plt.xlabel('Time', fontsize=18)
plt.title(file_name)
plt.rc('axes', titlesize=20)

plt.show()
"""
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

fig.savefig(results_dir + file_name + ".png")

#######################################################################
##########saving info as an excel file
#######################################################################

"""
# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pandas.ExcelWriter(results_dir + file_name+'.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df1.to_excel(writer, sheet_name='No EV')
#df2.to_excel(writer, sheet_name='EV')

# Close the Pandas Excel writer and output the Excel file.
writer.save()
"""