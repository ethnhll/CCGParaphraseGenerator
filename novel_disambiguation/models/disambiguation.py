from xml.etree import cElementTree as ElementTree

__author__ = 'Ethan A. Hill'


class Disambiguation:
    def __init__(self, full_id, disambiguation_type, realization, dependencies):
        self.full_id = full_id
        self.disambiguation_type = disambiguation_type
        self.realization = realization
        self.dependency_details_map = dependencies

    def is_valid(self):
        return self.realization != '' and self.disambiguation_type != ''

    def xmlize(self, ambiguous_span):
        attributes = {'parse_id': self.full_id,
                      'type': self.disambiguation_type,
                      'realization': self.realization,
                      'valid': str(self.is_valid())}
        disambig_xml = ElementTree.Element('disambiguation', attributes)
        info_xml = ElementTree.SubElement(disambig_xml, 'dependencies', )
        for info, unlabeled in self.dependency_details_map.iteritems():
            head, dependent = info
            if unlabeled in ambiguous_span:
                info_attributes = {
                    'head': str(dict(head._asdict())),
                    'dependent': str(dict(dependent._asdict())),
                    'ambiguous': 'True'}
            else:
                info_attributes = {
                    'head': str(dict(head._asdict())),
                    'dependent': str(dict(dependent._asdict())),
                    'ambiguous': 'False'}
            ElementTree.SubElement(info_xml, 'dependency', info_attributes)

        return disambig_xml