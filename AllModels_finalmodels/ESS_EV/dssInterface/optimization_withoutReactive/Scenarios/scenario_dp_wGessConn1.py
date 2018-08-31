# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 18:36:06 2018

@author: guemruekcue
"""

scenario_24Ts={}
scenario_24Ts['T']=24
scenario_24Ts['PV_Inv_Max_Power']= 10.0
scenario_24Ts['P_Grid_Max_Export_Power']= 10.0
scenario_24Ts['ESS_Min_SoC']=0.25
scenario_24Ts['ESS_Max_SoC']=0.95
scenario_24Ts['ESS_Capacity']= 9.6   #kWh
scenario_24Ts['ESS_Max_Charge_Power']= 6.2   #kW
scenario_24Ts['ESS_Max_Discharge_Power']= 6.2   #kW

#Forecasts  
scenario_24Ts['P_Load_Forecast']={0:   0.057,
                                 1:   0.0906,
                                 2:   0.0906,
                                 3:   0.070066667,
                                 4:	0.077533333,
                                 5:	0.0906,
                                 6:	0.0906,
                                 7:	0.10935,
                                 8:	0.38135,
                                 9:	1.473716667,
                                 10:	0.988183333,
                                 11:	2.4413,
                                 12:	0.4216,
                                 13:	0.21725,
                                 14:	0.4536,
                                 15:	0.4899,
                                 16:	0.092466667,
                                 17:	0.088733333,
                                 18:	0.0906,
                                 19:	0.47475,
                                 20:	0.48255,
                                 21:	1.051866667,
                                 22:	1.296316667,
                                 23:	0.200733333}
    
scenario_24Ts['P_PV_Forecast']={ 0: 0,
                                 1:	0,
                                 2:	0,
                                 3:	0,
                                 4:	0,
                                 5:	0,
                                 6:	0,
                                 7:	0,
                                 8:	1.13248512,
                                 9:	3.016735616,
                                 10:	4.823979947,
                                 11:	6.329861639,
                                 12:	7.06663104,
                                 13:	7.42742784,
                                 14:	7.420178035,
                                 15:	7.077290784,
                                 16:	5.99361984,
                                 17:	4.036273408,
                                 18:	1.462618829,
                                 19:	0,
                                 20:	0,
                                 21:	0,
                                 22:	0,
                                 23:	0} 
   
scenario_24Ts['Price_Forecast']={0 :  34.61,
                                1 :  33.28,
                                2 :  33.03,
                                3 :  32.93,
                                4 :  31.96,
                                5 :  33.67,
                                6 :  40.45,
                                7 :  47.16,
                                8 :  47.68,
                                9 :  46.23,
                                10:  43.01,
                                11:  39.86,
                                12:  37.64,
                                13:  37.14,
                                14:  39.11,
                                15:  41.91,
                                16:  44.11,
                                17:  48.02,
                                18:  51.65,
                                19:  48.73,
                                20:  43.56,
                                21:  38.31,
                                22:  37.66,
                                23:  36.31}

ess_soc_domain=[30,40,50,60,70,80,90]   
decision_domain=list(range(-60,70,10))
ini_soc=40

ess_command= {0:0.0,1:0.0,2:0.0,3:0.0,4:0.0,5:0.0,6:0.0,7:0.0,8:-0.8,9:-0.8,10:-0.8,11:-0.8,12:-0.8,13:-0.8,14:-0.8,15:-0.8,16:-0.8,17:-0.8,18:-0.8,19:1.0,20:1.0,21:1.0,22:1.0,23:1.0}
local_coef=dict.fromkeys(range(24),1)
global_coef=dict.fromkeys(range(24),1)

#%%
if __name__=="__main__":
    ess_command2={0:0.5,1:0.5,2:0.5,3:0.5,4:0.5,5:0.5,6: 0.0,7: 0.0,8: 0.0,9: 0.0,10: 0.0,11: 0.0,12: 0.0,13: 0.0,14: 0.0,15: 0.0,16: 0.0,17: 0.0,18: 0.5,19:0.5,20:0.5,21:0.5,22:0.5,23:0.5}
    ess_command3={0:0.7,1:0.7,2:0.7,3:0.7,4:0.7,5:0.7,6: 0.7,7: 0.7,8: 0.7,9: 0.7,10: 0.7,11: 0.7,12: 0.7,13: 0.7,14: 0.7,15: 0.7,16: 0.7,17: 0.7,18: 0.7,19:0.7,20:0.7,21:0.7,22:0.7,23:0.7}
    
    
    signal1=[]
    signal2=[]
    signal3=[]
    for key in range(24):
        for t in range(60):
            signal1.append(ess_command[key]/100*scenario_24Ts['ESS_Capacity'])
            signal2.append(ess_command2[key]/100*scenario_24Ts['ESS_Capacity'])
            signal3.append(ess_command3[key]/100*scenario_24Ts['ESS_Capacity'])
    import matplotlib.pylab as plt
    
    x=list(range(1440))
    
    fig1=plt.subplot(1,1,1)
    fig1.set_title('Different commands from GESSCON')
    plt.plot(x, signal1,label='signal1')
    plt.plot(x, signal2,label='signal2')
    plt.plot(x, signal3,label='signal3')
    plt.legend()
        
    plt.tight_layout()
    plt.savefig('Results_1.png')
    
    plt.show()
    

    