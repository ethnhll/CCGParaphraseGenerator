from xml.etree import cElementTree as ElementTree

__author__ = 'Ethan A. Hill'


class Reversal:

    def __init__(self, reparse_sentence_id, parent_file_name, realization):
        # Actually set separately from reparse, though they should coincide
        self.reparse_sentence_id = reparse_sentence_id
        self.parent_file_name = parent_file_name
        self.realization = realization
        self.reparse = None
        self.validated = None

    def is_validated(self):
        # Returns None if validate was not yet called
        return self.validated

    def validate(self, parent_parse, reparse, ambiguous_span):
        self.reparse = reparse
        parse_unlabeled = parent_parse.unlabeled_dependency_set()
        parse_specific_span = parse_unlabeled.intersection(ambiguous_span)
        # Get the ambiguity that didn't exist in the parse
        #unrelated_span = ambiguous_span.difference(parse_unlabeled)
        # Check if the parse specific ambiguous span exists in the reparse
        reparse_unlabeled = reparse.unlabeled_dependency_set()
        self.validated = parse_specific_span.issubset(reparse_unlabeled)
        #has_subset = parse_specific_span.issubset(reparse_unlabeled)
        # Now check if the reparse excludes the unrelated span
        #includes_unrelated = unrelated_span.issubset(reparse_unlabeled)
        #self.validated = has_subset and not includes_unrelated
        return self.validated

    def xmlize(self):
        attributes = {'type': 'reversal',
                      'realization': self.realization,
                      'valid': str(self.validated)}
        reversal_xml = ElementTree.Element('reversal', attributes)
        if self.reparse:
            reparse_xml = ElementTree.SubElement(
                reversal_xml, 'reparse_unlabeled_dependencies')
            for head, dependent in self.reparse.unlabeled_dependency_set():
                unlabeled_attributes = {
                    'head': head,
                    'dependent': dependent}
                dependency_xml = ElementTree.Element(
                    'dependency', unlabeled_attributes)
                reparse_xml.append(dependency_xml)
        return reversal_xml