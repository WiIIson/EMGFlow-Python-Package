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
fig, axs = plt.subplots(1, 5, figsize=(15*5,15), sharey=True)

RMS_smooth = SignalFilterer.ApplyRMSSmooth(test_data, 'EMG_zyg', 50)
axs[0].plot(RMS_smooth['Time'], RMS_smooth['EMG_zyg'])
axs[0].set_title('EMG_zyg - RMS smoothing filter')
axs[0].set_ylabel('Voltage (mV)')
axs[0].set_xlabel('Time (s)')

boxcar_smooth = SignalFilterer.ApplyBoxcarSmooth(test_data, 'EMG_zyg', 50)
axs[1].plot(boxcar_smooth['Time'], boxcar_smooth['EMG_zyg'])
axs[1].set_title('EMG_zyg - Boxcar smoothing filter')
axs[1].set_ylabel('Voltage (mV)')
axs[1].set_xlabel('Time (s)')

gaussian_smooth = SignalFilterer.ApplyGaussianSmooth(test_data, 'EMG_zyg', 50)
axs[2].plot(gaussian_smooth['Time'], gaussian_smooth['EMG_zyg'])
axs[2].set_title('EMG_zyg - Gaussian smoothing filter')
axs[2].set_ylabel('Voltage (mV)')
axs[2].set_xlabel('Time (s)')

loess_smooth = SignalFilterer.ApplyLoessSmooth(test_data, 'EMG_zyg', 50)
axs[3].plot(loess_smooth['Time'], loess_smooth['EMG_zyg'])
axs[3].set_title('EMG_zyg - Loess smoothing filter')
axs[3].set_ylabel('Voltage (mV)')
axs[3].set_xlabel('Time (s)')

spline_smooth = SignalFilterer.ApplySplineSmooth(test_data, 'EMG_zyg', 1)
axs[4].plot(spline_smooth['Time'], spline_smooth['EMG_zyg'])
axs[4].set_title('EMG_zyg - Spline smoothing filter')
axs[4].set_ylabel('Voltage (mV)')
axs[4].set_xlabel('Time (s)')

fig.suptitle('EMG_zyg - Smoothing comparisons')
fig.savefig('Plots/SmoothingMethods/Comparison.jpg')