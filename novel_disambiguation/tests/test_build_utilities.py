import os
import shutil
import unittest
import constant_values
from xml.etree import cElementTree as ElementTree

from ..constants import ccg_values
from ..utilities import build_utilities

__author__ = 'Ethan A. Hill'


class TestBuildUtilities(unittest.TestCase):
    # Since the parser is an external program, it is difficult to test for
    # specific behaviors and so each test involves many checks at once

    _original_working_directory = None

    @classmethod
    def setUpClass(cls):
        # Move to the ccgbank directory to start the process
        cls._original_working_directory = os.getcwd()
        ccgbank_expand = os.path.expandvars(ccg_values.CCGBANK_PATH)
        os.chdir(ccgbank_expand)


    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._original_working_directory)

    def test_ccg_build_parse_empty_text_file(self):
        empty_file_name = constant_values.TEST_EMPTY_TEXT_FILE
        expanded = os.path.expandvars(constant_values.FULL_PATH_DATA_NOVEL)

        empty_file_sub_path = os.path.join(
            constant_values.SUB_PATH_DATA_NOVEL, empty_file_name)
        full_empty_file_path = os.path.join(expanded, empty_file_name)
        empty_file_directory = '%s.dir' % full_empty_file_path

        # Remove the expected output directory if it exists, test for creation
        if os.path.exists(empty_file_directory):
            shutil.rmtree(empty_file_directory)
        # Run the parser, which assumes the file is at least in 'data/novel'
        output = build_utilities.ccg_build_parse(empty_file_sub_path)

        # Check if the output contains build success message
        self.assertIn(constant_values.BUILD_SUCCESS_MESSAGE, output)
        # Check that output doesn't contain any Exception messages
        self.assertNotIn(constant_values.EXCEPTION_MESSAGE, output)
        # Did the directory get created?
        self.assertTrue(
            os.path.exists(empty_file_directory), 'directory does not exist')

        # Check for existence of the logical form
        lf_path = os.path.join(
            empty_file_directory, constant_values.LOGICAL_FORM)
        self.assertTrue(os.path.exists(lf_path), 'logical form does not exist')
        lf_xml = ElementTree.parse(lf_path)
        # Check that the list of elements in the tree has only one element
        elements = list(lf_xml.iter())
        self.assertLessEqual(len(elements), 1)

    def test_ccg_build_parse_regular_text_file(self):
        # It is difficult to test this because even if a non-existent text
        # file is passed, build still occurs
        text_file = constant_values.TEST_ONE_SENTENCE_TEXT_FILE
        expanded = os.path.expandvars(constant_values.FULL_PATH_DATA_NOVEL)

        text_file_sub_path = os.path.join(
            constant_values.SUB_PATH_DATA_NOVEL, text_file)
        full_text_file_path = os.path.join(expanded, text_file)
        text_file_directory = '%s.dir' % full_text_file_path

        # Remove the expected output directory if it exists, test for creation
        if os.path.exists(text_file_directory):
            shutil.rmtree(text_file_directory)
        # Run the parser, which assumes the file is at least in 'data/novel'
        output = build_utilities.ccg_build_parse(text_file_sub_path)

        # Check if the output contains build success message
        self.assertIn(constant_values.BUILD_SUCCESS_MESSAGE, output)
        # Check that output doesn't contain any Exception messages
        self.assertNotIn(constant_values.EXCEPTION_MESSAGE, output)
        # Did the directory get created?
        self.assertTrue(
            os.path.exists(text_file_directory), 'directory does not exist')

        # Check for existence of the logical form
        lf_path = os.path.join(
            text_file_directory, constant_values.LOGICAL_FORM)
        self.assertTrue(os.path.exists(lf_path), 'logical form does not exist')
        lf_xml = ElementTree.parse(lf_path)
        # Check that the list of elements in the tree has at least one element
        elements = list(lf_xml.iter())
        self.assertGreaterEqual(len(elements), 1)

    def test_ccg_build_realize_existing_text_file(self):
        text_file = constant_values.DATA_SUB_TEST_SENTENCES
        output = build_utilities.ccg_build_realize(text_file)
        self.assertTrue(constant_values.TEST_BUILD_SUCCESSFUL in output,
                        'Did not successfully realize a text file...')
        self.assertTrue(constant_values.TEST_EXCEPTION not in output,
                        'Exception encountered while realizing text file...')
        # Did the realization file realize.nbest get created?
        expanded = os.path.expandvars(
            constant_values.FULL_PATH_TEST_REALIZATIONS)
        self.assertTrue(os.path.exists(expanded),
                        'Did not successfully create realize.nbest...')

if __name__ == '__main__':
    unittest.main()