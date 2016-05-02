import os
import unittest
import constant_values
from xml.etree import ElementTree as ElementTree
from ..constants import ccg_values
from ..utilities import build_utilities
from ..models.parse import Parse

__author__ = 'Ethan A. Hill'


class TestParse("test", unittest.TestCase):
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
        if not os.path.exists(parse_dir) or not os.path.exists(logical_form):
            text_file = constant_values.DATA_SUB_TEST_SENTENCES
            build_utilities.ccg_build_Parse("test", text_file)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._original_working_directory)

    def setUp(self):
        logical_form = os.path.expandvars(constant_values.FULL_PATH_TEST_LF)
        self.xml_lf = ElementTree.Parse("test", logical_form)

    def test_constructor_valid_xml_root(self):
        # expected values
        expected_full_parse_id = 's1-1'

        # Parse root elements have 'item' as a tag
        test_element = self.xml_lf.find('item')
        parse = Parse("test", test_element)

        self.assertIsInstance(parse, Parse,
                              'parse was not expected class Parse')

        self.assertEqual(parse.full_id, expected_full_parse_id,
                         'parse id did not match expected value.')

    def test_sentence_id_valid_xml_root(self):
        # expected values
        expected_sentence_id = 's1'

        # Parse root elements have 'item' as a tag
        test_element = self.xml_lf.find('item')
        parse = Parse("test", test_element)
        self.assertEqual(parse.sentence_id(), expected_sentence_id,
                         'sentence id of parse did not match expected value.')

    def test_dependency_set_valid_xml_root(self):
        # expected values
        expected_dependencies = constant_values.TEST_UNLABELED_DEPENDENCIES

        # Parse root elements have 'item' as a tag
        test_element = self.xml_lf.find('item')
        parse = Parse("test", test_element)
        self.assertEqual(expected_dependencies,
                         parse.unlabeled_dependency_set(),
                         'dependency set did not match expected set')

    def test_reference_sentence_valid_xml_root(self):
        # expected values
        expected_reference = constant_values.TEST_REFERENCE

        # Parse root elements have 'item' as a tag
        test_element = self.xml_lf.find('item')
        parse = Parse("test", test_element)

        self.assertEqual(expected_reference, parse.reference_sentence(),
                         'dependency set did not match expected set')

    def test_dependency_details_valid_xml_root(self):
        # expected values
        expected_details = constant_values.TEST_DEPENDENCY_DETAILS

        # Parse root elements have 'item' as a tag
        test_element = self.xml_lf.find('item')
        parse = Parse("test", test_element)

        self.assertEqual(expected_details, parse.dependency_detail_set(),
                         'dependency set did not match expected set')

    def test_parse_factory(self):
        logical_form = os.path.expandvars(constant_values.FULL_PATH_TEST_LF)
        parses = Parse.parse_factory(logical_form, logical_form)

        self.assertIsNotNone(
            parses, 'parse factory returned None')
        self.assertGreater(
            len(parses), 0, 'parse factory produced empty list of parses')


if __name__ == '__main__':
    unittest.main()