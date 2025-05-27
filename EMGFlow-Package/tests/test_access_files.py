import unittest
import os
import shutil

from src.EMGFlow.access_files import *

import pandas as pd

#
# =============================================================================
#

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        pass
    
#
# =============================================================================
#
    
    def test_make_paths(self):
        pathNames = make_paths()
        self.assertIsInstance(pathNames, dict)
        self.assertTrue(os.path.isdir('Data'))
    
    def test_make_sample_data(self):
        pathNames = make_paths()
        EMGFlow.make_sample_data(pathNames)
        self.assertTrue(os.path.exists(os.path.join('Data', 'Raw', '01', 'sample_data_01.csv')))
        self.assertTrue(os.path.exists(os.path.join('Data', 'Raw', '01', 'sample_data_02.csv')))
        self.assertTrue(os.path.exists(os.path.join('Data', 'Raw', '02', 'sample_data_03.csv')))
        self.assertTrue(os.path.exists(os.path.join('Data', 'Raw', '02', 'sample_data_04.csv')))
    
    def test_read_file_type(self):
        pathNames = make_paths()
        make_sample_data(pathNames)
        df = read_file_type(os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv'), 'csv')
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_map_files(self):
        pathNames = make_paths()
        make_sample_data(pathNames)
        filedirs = map_files(pathNames['Raw'])
        self.assertIsInstance(filedirs, dict)
    
    def test_convert_map_files(self):
        pathNames = make_paths()
        make_sample_data(pathNames)
        filedirs = convert_map_files(pathNames['Raw'])
        filedirs = convert_map_files(filedirs)
        self.assertIsInstance(filedirs, dict)
    
    def test_map_files_fuse(self):
        pathNames = make_paths()
        make_sample_data(pathNames)
        pathDF = map_files_fuse([pathNames, pathNames], ['test1', 'test2'])
        self.assertIsInstance(pathDF, pd.DataFrame)
    
#
# =============================================================================
#

    def tearDown(self):
        if os.path.exists('./Data') == True:
            shutil.rmtree('./Data')

#
# =============================================================================
#

if __name__ == '__main__':
    unittest.main()