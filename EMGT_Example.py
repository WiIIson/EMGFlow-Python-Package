import EMGT

raw_path = 'Data/01_Raw/'
notch_path = 'Data/02_Notch/'
notch_s_path = 'Data/02_Notch_Special/'
bandpass_path = 'Data/03_Bandpass/'
smooth_path = 'Data/04_Smooth/'
feature_path = 'Data/05_Feature/'

sampling_rate = 2000
cols = ['EMG_zyg', 'EMG_cor']

notch_vals = [(50,5), (150,25), (250,25), (350,25), (400,25), (450,25), (550,25), (650,25), (750,25), (850,25), (950,25)]

notch_sc = [(317, 25)]
reg = "^(08|11)"

EMGT.SignalFilterer.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols, exp_copy=True)
EMGT.SignalFilterer.NotchFilterSignals(notch_path, notch_s_path, sampling_rate, notch_sc, cols, expression=reg, exp_copy=True)
EMGT.SignalFilterer.BandpassFilterSignals(notch_s_path, bandpass_path, sampling_rate, 20, 450, cols, exp_copy=True)
EMGT.SignalFilterer.SmoothFilterSignals(bandpass_path, smooth_path, sampling_rate, 50, exp_copy=True)
EMGT.SignalFilterer.AnalyzeSignals(bandpass_path, smooth_path, feature_path, sampling_rate, cols=cols)