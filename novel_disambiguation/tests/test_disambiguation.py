import os
import unittest
from ..utilities import disambig_utilities
from ..utilities import build_utilities
from ..constants import ccg_values
from ..tests import constant_values

__author__ = 'hill1303'


class TestDisambiguation(unittest.TestCase):
    _original_working_directory = None

    @classmethod
    def setUpClass(cls):
        # Move to the ccgbank directory to start the process
        cls._original_working_directory = os.getcwd()
        ccgbank_expanded = os.path.expandvars(ccg_values.CCGBANK_PATH)
        os.chdir(ccgbank_expanded)
        # Generate the logical form if it doesn't exist
        parse_dir = os.path.expandvars(constant_values.FULL_PATH_TEST_DIR)
        logical_form = os.path.expandvars(constant_values.FULL_PATH_TEST_LF)
        real = os.path.expandvars(constant_values.FULL_PATH_TEST_REALIZATIONS)
        text_file = constant_values.DATA_SUB_TEST_SENTENCES
        if not os.path.exists(parse_dir) or not os.path.exists(logical_form):
            build_utilities.ccg_build_parse(text_file)
        if not os.path.exists(real):
            build_utilities.ccg_build_realize(text_file)


    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._original_working_directory)

    def setUp(self):
        path_to_text = constant_values.DATA_SUB_TEST_SENTENCES
        self.path_to_text = os.path.expandvars(path_to_text)

    def test_disambiguate_post_process_false(self):
        disambig_utilities.disambiguate(self.path_to_text, False)

    def test_disambiguate_post_process_true(self):
        disambig_utilities.disambiguate(self.path_to_text, True)

if __name__ == '__main__':
    unittest.main()
