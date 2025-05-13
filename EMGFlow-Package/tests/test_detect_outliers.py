import unittest
import importlib
import os
import shutil

# Load EMGFlow from local files
filePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'EMGFlow', '__init__.py'))
spec = importlib.util.spec_from_file_location("EMGFlow", filePath)
EMGFlow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(EMGFlow)

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
        outliers = EMGFlow.detect_outliers(pathNames['Raw'], 2000, 2, windowSize=20)
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