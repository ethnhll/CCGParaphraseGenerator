__author__ = 'Ethan A. Hill'
from xml.etree import cElementTree as ElementTree


class Rewrite():
    def __init__(self, rewrite_id, validation_map):
        self.full_id = rewrite_id
        # This is used in setting up a correspondence for the realization
        self.validation_map = validation_map

        self.is_valid = None
        self.realization = None

    def type_of_change(self):
        parse_id, rewrite_type = self.full_id.split('#')
        return rewrite_type

    def parse_id(self):
        parse_id, rewrite_type = self.full_id.split('#')
        return parse_id

    def xmlize(self):
        attributes = {'type': self.type_of_change(),
                      'realization': self.realization,
                      'valid': str(self.is_valid)}
        rewrite_xml = ElementTree.Element('rewrite', attributes)
        return rewrite_xml