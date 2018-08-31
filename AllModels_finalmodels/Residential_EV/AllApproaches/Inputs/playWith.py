# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 17:52:13 2018

@author: guemruekcue
"""

import pandas as pd

xl= pd.ExcelFile("GessCon_60M.xlsx")

df={}
df[0]  = xl.parse("S4G")

writer = pd.ExcelWriter('GessCon_60M2.xlsx')
df[0].to_excel(writer,str(0))


for n in range(1,24):
    df[n]=df[n-1].shift(periods=-1)
    df[n].loc[23]=df[n-1].loc[0]
    df[n].to_excel(writer,str(n))

writer.save()
    