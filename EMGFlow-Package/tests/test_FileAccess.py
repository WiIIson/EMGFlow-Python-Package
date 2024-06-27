import unittest
import pandas as pd
import sys
import numpy as np
import os

from src.EMGFlow.FileAccess import *

test_df = pd.DataFrame({'r1':[1,2,4,2,5,3,1,5,7,3,7,8,4,2,5,3,5,3,2,1,6,3,6,1,2]})
test_df_2 = pd.DataFrame({'r1':[1,-2,3,-4,5,6,-7]})
test_sr = 1000

#
# =============================================================================
#

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

#
# =============================================================================
#
        
    def test_ReadFileType(self):
        df = ReadFileType('./Testing/Data.csv', 'csv')
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_MapFiles(self):
        dic = MapFiles('./Testing')
        self.assertEqual(list(dic.keys()), ['Data.csv'])
    
    def test_ConvertMapFiles(self):
        dic = ConvertMapFiles('./Testing')
        self.assertEqual(list(dic.keys()), ['Data.csv'])
    
    def test_MapFilesFuse(self):
        f1 = {'f1': 'data/raw/file1.csv', 'f2': 'data/raw/file2.csv'}
        f2 = {'f1': 'data/notch/file1.csv', 'f2': 'data/notch/file2.csv'}
        mf = MapFilesFuse([f1, f2], ['raw', 'notch'])
        ans = pd.DataFrame({'File': ['f1', 'f2'],
                            'ID': ['f1', 'f2'],
                            'raw':['data/raw/file1.csv', 'data/raw/file2.csv'],
                            'notch': ['data/notch/file1.csv', 'data/notch/file2.csv']}).set_index('ID')
        self.assertTrue(ans.equals(mf))

#
# =============================================================================
#

    def tearDown(self):
        if os.path.exists('./Testing') == True:
            os.remove('./Testing/Data.csv')
            os.rmdir('./Testing')
        if os.path.exists('./Testing_out') == True:
            os.rmdir('./Testing_out')
        if os.path.exists('./Testing_plots') == True:
            os.rmdir('./Testing_plots')