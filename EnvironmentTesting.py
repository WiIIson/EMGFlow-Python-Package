# Relevant libraries
import neurokit2 as nk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Environment libraries
import SignalFilterer
import PlotSubjects
import OutlierFinder

# Constants
sr = 2000
Hzs = [50, 150, 250, 350, 450, 400, 550, 650, 750, 850, 950]
Qs =  [ 5,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]

# Sample subjects
s10_1 = 'Data/Raw-Data/Raw_PID_01-10/10/10-01-01.csv'
s10_2 = 'Data/Raw-Data/Raw_PID_01-10/10/10-02-01.csv'
s10_3 = 'Data/Raw-Data/Raw_PID_01-10/10/10-03-01.csv'
s24_7 = 'Data/Raw-Data/Raw_PID_21-30/24/24-07-03.csv'

#
# =============================================================================
#

# Load and clean data
test_data = pd.read_csv(s10_1)
test_data = SignalFilterer.ApplyNotchFilters(test_data, 'EMG_zyg', Hzs, Qs, sr)
test_data = SignalFilterer.ApplyBandpassFilter(test_data, 'EMG_zyg', 20, 450, sr)
test_data = SignalFilterer.ApplyFWR(test_data, 'EMG_zyg')

# Apply different smoothing filters and create plots

RMS_smooth = SignalFilterer.ApplyRMSSmooth(test_data, 'EMG_zyg', 50)
plt.plot(RMS_smooth['Time'], RMS_smooth['EMG_zyg'])
plt.title('EMG_zyg - RMS smoothing filter')
plt.ylabel('Voltage (mV)')
plt.xlabel('Time (s)')
plt.savefig('Plots/SmoothingMethods/RMS_smoothing_filter.png')
plt.clf()

boxcar_smooth = SignalFilterer.ApplyBoxcarSmooth(test_data, 'EMG_zyg', 50)
plt.plot(boxcar_smooth['Time'], boxcar_smooth['EMG_zyg'])
plt.title('EMG_zyg - Boxcar smoothing filter')
plt.ylabel('Voltage (mV)')
plt.xlabel('Time (s)')
plt.savefig('Plots/SmoothingMethods/boxcar_smoothing_filter.png')
plt.clf()

loess_smooth = SignalFilterer.ApplyLoessSmooth(test_data, 'EMG_zyg', 50)
plt.plot(loess_smooth['Time'], loess_smooth['EMG_zyg'])
plt.title('EMG_zyg - Loess smoothing filter')
plt.ylabel('Voltage (mV)')
plt.xlabel('Time (s)')
plt.savefig('Plots/SmoothingMethods/loess_smoothing_filter.png')
plt.clf()