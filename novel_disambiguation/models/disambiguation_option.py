from xml.etree import cElementTree as ElementTree

__author__ = 'Ethan A. Hill'


class DisambiguationOption:
    REVERSAL = 'reversal'

    def __init__(self, sentence):
        self.parent_text_file_name = sentence.parent_file_name
        self.sentence_id = sentence.full_id
        self.reference = sentence.reference
        self.ambiguity = sentence.ambiguous_span()
        self.disambiguations = []

    def single_sided_option(self):
        if len(self.disambiguations) == 2:
            disambig, other_disambig = self.disambiguations
            single_sided_left = (disambig.is_valid() and not
                                 other_disambig.is_valid())
            single_sided_right = (other_disambig.is_valid() and not
                                  disambig.is_valid())
            return single_sided_left or single_sided_right
        # This should not really happen
        return False

    def double_sided_option(self):
        if len(self.disambiguations) == 2:
            disambig, other_disambig = self.disambiguations
            return disambig.is_valid() and other_disambig.is_valid()
        # This should not really happen
        return False

    def xmlize(self):
        attributes = {
            'text_file': str(self.parent_text_file_name),
            'sentence_id': self.sentence_id,
            'double_sided': str(self.double_sided_option()),
            'reference': self.reference}
        option_xml = ElementTree.Element('option', attributes)
        sub_xml = ElementTree.SubElement(option_xml, 'dependencies')
        # attach the ambiguous span now
        for head, dependent in self.ambiguity:
            dependency = {'head': head, 'dependent': dependent}
            ElementTree.SubElement(sub_xml, 'dependency', dependency)
        for disambig in self.disambiguations:
            option_xml.append(disambig.xmlize(self.ambiguity))

        return option_xml
