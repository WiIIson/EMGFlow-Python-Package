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
test_data = pd.read_csv(s10_1)
test_data = SignalFilterer.ApplyNotchFilters(test_data, 'EMG_zyg', Hzs, Qs, sr)
test_data = SignalFilterer.ApplyBandpassFilter(test_data, 'EMG_zyg', 20, 450, sr)
#test_data = SignalFilterer.ApplyFWR(test_data, 'EMG_zyg')
#test_data = SignalFilterer.ApplyRMSSmooth(test_data, 'EMG_zyg', 50)
#test_data = SignalFilterer.ApplyBandpassFilter(test_data, 'EMG_zyg', 20, 450, sr)


plt.plot(test_data['Time'], test_data['EMG_zyg'])
plt.ylabel('Power (mV)')
plt.xlabel('Time (s)')
plt.show()

psd_zyg = nk.signal_psd(test_data['EMG_zyg'], sampling_rate=sr)

val = SignalFilterer.CalcSpecFlux(test_data, test_data, 'EMG_zyg', 'EMG_zyg', sr, sr)
print(val)

print(np.array(psd_zyg['Power']) + 4)
plt.plot(psd_zyg['Frequency'], psd_zyg['Power'])
plt.show()