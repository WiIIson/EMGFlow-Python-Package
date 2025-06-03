import unittest
import os
import shutil

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

    def test_detect_outliers(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        outliers = EMGFlow.detect_spectral_outliers(pathNames['Raw'], 2000, 2, window_size=15)
        self.assertIsInstance(outliers, dict)

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