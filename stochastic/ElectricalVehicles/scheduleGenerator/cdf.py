# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 11:56:48 2018

@author: guemruekcue
"""

import numpy as np
import scipy.stats
import matplotlib.pyplot as plt


"""
mu_leave, sigma_leave = 571.47, 203.3597
mu_arrival, sigma_arrival = 1036.89172, 195.6852
mu_eleCon, sigma_eleCon = 6.756456347, 4.177621543

mu_leave, sigma_leave = 554.9276316, 196.4975869
mu_arrival, sigma_arrival = 1056.996711, 189.5963316
mu_eleCon, sigma_eleCon = 8.384973792, 5.258704604
"""
mu_leave, sigma_leave = 554.511254, 196.1607447
mu_arrival, sigma_arrival = 1058.491961, 189.5043257
mu_eleCon, sigma_eleCon = 8.81587686, 5.935570589


pdf_leave=scipy.stats.norm(mu_leave, sigma_leave)
pdf_arrival=scipy.stats.norm(mu_arrival, sigma_arrival)
pdf_eleCon=scipy.stats.norm(mu_eleCon, sigma_eleCon)

print("First leave probabilities")
print("Between 00:00 and 06:00:",pdf_leave.cdf(6*60))
print("Between 06:00 and 12:00:",pdf_leave.cdf(12*60)-pdf_leave.cdf(6*60))
print("Between 12:00 and 18:00:",pdf_leave.cdf(18*60)-pdf_leave.cdf(12*60))
print("Between 18:00 and 24:00:",pdf_leave.cdf(24*60)-pdf_leave.cdf(18*60))
print()

print("Last arrival probabilities")
veryEarly=pdf_arrival.cdf(14*60)
Early=pdf_arrival.cdf(18*60)-pdf_arrival.cdf(14*60)
Normal=pdf_arrival.cdf(22*60)-pdf_arrival.cdf(18*60)
Late=pdf_arrival.cdf(24*60)-pdf_arrival.cdf(22*60)
print("Between 00:00 and 14:00:",pdf_arrival.cdf(14*60))
print("Between 14:00 and 18:00:",pdf_arrival.cdf(18*60)-pdf_arrival.cdf(14*60))
print("Between 18:00 and 22:00:",pdf_arrival.cdf(22*60)-pdf_arrival.cdf(18*60))
print("Between 22:00 and 24:00:",pdf_arrival.cdf(24*60)-pdf_arrival.cdf(22*60))
print()

print("DOD")
HighSOC=pdf_eleCon.cdf(7.5)
MedSOC=pdf_eleCon.cdf(15)-pdf_eleCon.cdf(7.5)
LowSOC=pdf_eleCon.cdf(22.5)-pdf_eleCon.cdf(15)
VLowSOC=pdf_eleCon.cdf(30)-pdf_eleCon.cdf(22.5)

print("Between 00-25% :",pdf_eleCon.cdf(7.5))
print("Between 25-50% :",pdf_eleCon.cdf(15)-pdf_eleCon.cdf(7.5))
print("Between 50-75% :",pdf_eleCon.cdf(22.5)-pdf_eleCon.cdf(15))
print("Between 75-100%:",pdf_eleCon.cdf(30)-pdf_eleCon.cdf(22.5))
print()

earlyLow=Early*LowSOC
earlyMed=Early*MedSOC
earlyHigh=Early*HighSOC
normalLow=Normal*LowSOC
normalMed=Normal*MedSOC
normalHigh=Normal*HighSOC
lateLow=Late*LowSOC
lateMed=Late*MedSOC
lateHigh=Late*HighSOC

norm=1/(earlyLow+earlyMed+earlyHigh+normalLow+normalMed+normalHigh+lateLow+lateMed+lateHigh)

normalized_earlyLow=earlyLow*norm
normalized_earlyMed=earlyMed*norm
normalized_earlyHigh=earlyHigh*norm
normalized_normalLow=normalLow*norm
normalized_normalMed=normalMed*norm
normalized_normalHigh=normalHigh*norm
normalized_lateLow=lateLow*norm
normalized_lateMed=lateMed*norm
normalized_lateHigh=lateHigh*norm

normalized_sum=normalized_earlyLow+normalized_earlyMed+normalized_earlyHigh+normalized_normalLow+normalized_normalMed+normalized_normalHigh+normalized_lateLow+normalized_lateMed+normalized_lateHigh

print(normalized_sum)