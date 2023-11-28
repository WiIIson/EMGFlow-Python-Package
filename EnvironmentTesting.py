# Relevant libraries
import neurokit2 as nk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Environment libraries
import SignalFilterer
import PlotSubjects
import OutlierFinder

# Constants (agreed upon)
sr = 2000
Hzs = [50, 150, 250, 350, 450, 400, 550, 650, 750, 850, 950]
Qs =  [ 5,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]

# Sample subjects
s10_1 = 'Data/01_Raw/Raw_PID_01-10/10/10-01-01.csv'
s10_2 = 'Data/01_Raw/Raw_PID_01-10/10/10-02-01.csv'
s10_3 = 'Data/01_Raw/Raw_PID_01-10/10/10-03-01.csv'
s24_7 = 'Data/01_Raw/Raw_PID_21-30/24/24-07-03.csv'

#
# =============================================================================
#

# Load and clean data
test_data1 = pd.read_csv(s10_1)
test_data2 = pd.read_csv(s10_3)


ans1 = SignalFilterer.CalcSpecFlux(test_data1, 0.5, 'EMG_cor', sr)

print(ans1)

ans2 = SignalFilterer.CalcSpecFlux(test_data2, 0.5, 'EMG_cor', sr)

print(ans2)

ans3 = SignalFilterer.CalcSpecFlux(test_data1, test_data2, 'EMG_cor', sr)

print(ans3)