import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append('..')

#from EMGFlow.OutlierFinder import *
#from EMGFlow.PreprocessSignals import EMG2PSD

from src.EMGFlow.OutlierFinder import *
from src.EMGFlow.PreprocessSignals import EMG2PSD

class TestSimple(unittest.TestCase):
    
    def setUp(self):
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
    
    def test_DetectOutliers(self):
        
        with self.assertRaises(Exception):
            DetectOutliers('./Testing', -4, 5, window_size=5)
            
        with self.assertRaises(Exception):
            DetectOutliers('./Testing', 100, -5, window_size=5)
        
        with self.assertRaises(Exception):
            DetectOutliers('./Testing', 100, 5, expression='[', window_size=5)
        
        with self.assertRaises(Exception):
            DetectOutliers('./Testing', 100, 5, metric=np.mat, window_size=5)
            
        outliers = DetectOutliers('./Testing', 100, 5, window_size=5)
        self.assertIsInstance(outliers, dict)

    def tearDown(self):
        if os.path.exists('./Testing') == True:
            os.remove('./Testing/Data.csv')
            os.rmdir('./Testing')
        if os.path.exists('./Testing_out') == True:
            os.rmdir('./Testing_out')
        if os.path.exists('./Testing_plots') == True:
            os.rmdir('./Testing_plots')
