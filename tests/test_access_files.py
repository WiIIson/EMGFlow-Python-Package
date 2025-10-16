import unittest
import os
import shutil
import pandas as pd

import EMGFlow

#
# =============================================================================
#

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        pass
    
#
# =============================================================================
#

    def test_package_version(self):
        EMGFlow.package_version()
    
    def test_package_citation(self):
        EMGFlow.package_citation()
    
    def test_make_paths(self):
        pathNames = EMGFlow.make_paths()
        self.assertIsInstance(pathNames, dict)
        self.assertTrue(os.path.isdir('Data'))
    
    def test_make_sample_data(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        self.assertTrue(os.path.exists(os.path.join(pathNames['raw'], '01', 'sample_data_01.csv')))
        self.assertTrue(os.path.exists(os.path.join(pathNames['raw'], '01', 'sample_data_02.csv')))
        self.assertTrue(os.path.exists(os.path.join(pathNames['raw'], '02', 'sample_data_03.csv')))
        self.assertTrue(os.path.exists(os.path.join(pathNames['raw'], '02', 'sample_data_04.csv')))
    
    def test_read_file_type(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        df = EMGFlow.read_file_type(os.path.join(pathNames['raw'], '01', 'sample_data_01.csv'), 'csv')
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_map_files(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filedirs = EMGFlow.map_files(pathNames['raw'])
        self.assertIsInstance(filedirs, dict)
    
    def test_map_files_fuse(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        pathDF = EMGFlow.map_files_fuse([pathNames, pathNames], ['test1', 'test2'])
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