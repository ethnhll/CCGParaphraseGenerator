import os
import unittest
import constant_values
from ..constants import ccg_values
from ..utilities import build_utilities
from xml.etree import ElementTree
from ..models.parse import Parse
from ..models.sentence import Sentence

__author__ = 'Ethan A. Hill'


class TestSentence(unittest.TestCase):
    _original_working_directory = None

    @classmethod
    def setUpClass(cls):
        # Move to the ccgbank directory to start the process
        cls._original_working_directory = os.getcwd()
        ccgbank_expand = os.path.expandvars(ccg_values.CCGBANK_PATH)
        os.chdir(ccgbank_expand)
        # Generate the logical form if it doesn't exist
        parse_dir = os.path.expandvars(constant_values.FULL_PATH_TEST_DIR)
        logical_form = os.path.expandvars(constant_values.FULL_PATH_TEST_LF)
        if not os.path.exists(parse_dir) or not os.path.exists(logical_form):
            text_file = constant_values.DATA_SUB_TEST_SENTENCES
            build_utilities.ccg_build_parse(text_file)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._original_working_directory)

    def setUp(self):
        logical_form = os.path.expandvars(constant_values.FULL_PATH_TEST_LF)
        xml_lf = ElementTree.parse(logical_form)
        # Parse root elements have 'item' as a tag
        test_element = xml_lf.find('item')
        self.test_top_parse = Parse(logical_form, test_element)

    def test_constructor_valid_no_second_parse(self):

        sentence = Sentence(constant_values.TEST_TEXT_FILE,
                            self.test_top_parse)
        self.assertEqual(sentence.full_id, 's1',
                         'sentence id did not match expected id')
        self.assertEqual(sentence.parent_file_name,
                         constant_values.TEST_TEXT_FILE,
                         'parent file name did not match expected value')
        self.assertSetEqual(sentence.ambiguous_span(), set(),
                            'ambiguous span was not empty as expected')


if __name__ == '__main__':
    unittest.main()