import neurokit2 as nk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Sample subjects
s10_1 = 'Data/Raw-Data/Raw_PID_01-10/10/10-01-01.csv'
s10_2 = 'Data/Raw-Data/Raw_PID_01-10/10/10-02-01.csv'
s10_3 = 'Data/Raw-Data/Raw_PID_01-10/10/10-03-01.csv'
s24_7 = 'Data/Raw-Data/Raw_PID_21-30/24/24-07-03.csv'
sr = 2000

# Load subject data
sub_dat = pd.read_csv(s24_7)

# Process signals
#emg = sub_dat['EMG_zyg']
#emg_signals, info = nk.emg_process(emg, sampling_rate=sr)

print(np.unique(sub_dat['Events']))

plt.plot(sub_dat['Time'], sub_dat['Events'])

# Find events
#events = nk.events_find(sub_dat['Events'])

# Create epochs
#epochs = nk.epochs_create(emg_signals, events, sampling_rate=sr)

# Perform analysis
#analysis = nk.emg_eventrelated(epochs)