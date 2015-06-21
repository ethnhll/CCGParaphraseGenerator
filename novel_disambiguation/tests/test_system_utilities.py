import unittest
from ..utilities import system_utilities

__author__ = 'Ethan A. Hill'


class TestSystemUtilities(unittest.TestCase):
    def test_max_ram_usage(self):
        ram_usage = system_utilities.maximum_ram_usage()
        self.assertGreater(
            ram_usage, 0, 'maximum ram usable by ccg-build tasks is 0')
        self.assertGreaterEqual(
            ram_usage, 1, 'maximum ram usable by ccg-build tasks less than 1')

if __name__ == '__main__':
    unittest.main()
