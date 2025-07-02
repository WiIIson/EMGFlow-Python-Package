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