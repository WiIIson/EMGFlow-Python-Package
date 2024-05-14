import unittest
import pandas as pd
import numpy as np
import shiny

from EMGFlow.PlotSignals import *

in_path = ''
out_path = ''
sampling_rate = 2000

def setup_test():
    if os.path.exists('./Testing') == False:
        os.mkdir('./Testing')
        time_col = np.array(range(500)) / 100
        emg_col = np.sin(time_col) + (np.random.rand(500)/10)
        df = pd.DataFrame({'Time':time_col, 'EMG':emg_col})
        df.to_csv('./Testing/Data.csv', index=False)
    if os.path.exists('./Testing_out') == False:
        os.mkdir('./Testing_out')
    if os.path.exists('./Testing_plots') == False:
        os.mkdir('./Testing_plots')

class TestSimple(unittest.TestCase):
    
    def test_PlotSpectrum(self):
        PlotSpectrum('./Testing', './Testing_plots', 100, cols=['EMG'])
        os.remove('./Testing_plots/Data.jpg')
    
    def test_PlotCompareSignals(self):
        PlotCompareSignals('./Testing', './Testing', './Testing_plots', 100)
        os.remove('./Testing_plots/Data.jpg')
    
    def test_GenPlotDash(self):
        app = GenPlotDash(['./Testing'], 'EMG', 'mV', ['Test'], autorun=False)
        self.assertIsInstance(app, shiny.App)
    
if __name__ == '__main__':
    setup_test()
    unittest.main()