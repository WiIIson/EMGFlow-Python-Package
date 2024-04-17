import PlotSignals as EPLT

raw_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/01_Raw/'
notch_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch/'
notch_s_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch_Special/'
bandpass_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/03_Bandpass/'
smooth_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/04_Smooth/'
feature_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/05_Feature/'
plot_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/00_Plot/'

sampling_rate = 2000

in_paths = [smooth_path, bandpass_path, notch_s_path]
names = ['Smooth', 'Bandpass', 'Notch']

EPLT.GenPlotDash(in_paths, sampling_rate, 'EMG_zyg', 'mV', names)