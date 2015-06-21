from xml.etree import cElementTree as ElementTree

__author__ = 'Ethan A. Hill'


class Sentence:

    def __init__(self, parent_file_name, top_parse, next_best_parse=None):
        self.parent_file_name = parent_file_name
        self.top_parse = top_parse
        self.next_best_parse = next_best_parse
        self.reference = top_parse.reference_sentence()
        self.full_id = top_parse.sentence_id()

    def __repr__(self):
        repr_rep = ('Sentence(parent_file_name: {!s}, '
                      'full_id: {!s}, top_parse: {!s},'
                      'next_best_parse: {!s}'.format(self.parent_file_name,
                                                     self.full_id,
                                                     self.top_parse,
                                                     self.next_best_parse))
        return repr_rep

    def __cmp__(self, other):
        sentence_number = int(self.full_id[1:])
        other_sentence_number = int(other.full_id[1:])

        if self.parent_file_name == other.parent_file_name:
            return cmp(sentence_number, other_sentence_number)
        else:
            return cmp(self.parent_file_name, other.parent_file_name)

    def __eq__(self, other):
        return (self.parent_file_name == other.parent_file_name and
                self.full_id == other.full_id and
                self.top_parse == other.top_parse and
                self.next_best_parse == other.next_best_parse)

    def __ne__(self, other):
        return (self.parent_file_name != other.parent_file_name or
                self.full_id != other.full_id or
                self.top_parse != other.top_parse or
                self.next_best_parse != other.next_best_parse)

    def __lt__(self, other):
        sentence_number = int(self.full_id[1:])
        other_sentence_number = int(other.full_id[1:])

        if self.parent_file_name == other.parent_file_name:
            return sentence_number < other_sentence_number
        else:
            return self.parent_file_name < other.parent_file_name

    def __gt__(self, other):
        sentence_number = int(self.full_id[1:])
        other_sentence_number = int(other.full_id[1:])

        if self.parent_file_name == other.parent_file_name:
            return sentence_number > other_sentence_number
        else:
            return self.parent_file_name > other.parent_file_name

    def __le__(self, other):
        sentence_number = int(self.full_id[1:])
        other_sentence_number = int(other.full_id[1:])

        if self.parent_file_name == other.parent_file_name:
            return sentence_number <= other_sentence_number
        else:
            return self.parent_file_name <= other.parent_file_name

    def __ge__(self, other):
        sentence_number = int(self.full_id[1:])
        other_sentence_number = int(other.full_id[1:])

        if self.parent_file_name == other.parent_file_name:
            return sentence_number >= other_sentence_number
        else:
            return self.parent_file_name >= other.parent_file_name

    def ambiguous_span(self):
        if self.top_parse is not None and self.next_best_parse is not None:
            dependencies = self.top_parse.unlabeled_dependency_set()
            other_depend = self.next_best_parse.unlabeled_dependency_set()
            difference = dependencies.symmetric_difference(other_depend)
        else:
            # If there is no second parse, then there is no ambiguity
            difference = set()
        return difference

    def is_ambiguous(self):
        return True if self.ambiguous_span() else False

    def is_unambiguous(self):
        return True if not self.ambiguous_span() else False

    def detailed_ambiguous_span(self):
        span = self.ambiguous_span()
        # Only look at existing parses
        parses = [p for p in [self.top_parse, self.next_best_parse] if p]
        detailed_span = set()
        for parse in parses:
            for details, unlabeled in parse.dependency_details_map.iteritems():
                if unlabeled in span:
                    detailed_span.add(details)
        return detailed_span

    def parse_specific_ambiguity_details(self, parse):
        index_stem_map = {}
        for head, dependent in self.detailed_ambiguous_span():
            head_stem, head_pos = head.stem, head.pos_tag
            depend_stem, depend_pos = dependent.stem, dependent.pos_tag
            if (head, dependent) not in parse.dependency_details_map:
                # Adjust the stems that appear in the map to match parse stems
                for parse_head, parse_depend in parse.dependency_details_map:
                    if parse_head.index == head.index:
                        head_stem = parse_head.stem
                        head_pos = parse_head.pos_tag
                    elif parse_head.index == dependent.index:
                        depend_stem = parse_head.stem
                        depend_pos = parse_head.pos_tag
                    if parse_depend.index == head.index:
                        head_stem = parse_depend.stem
                        head_pos = parse_depend.pos_tag
                    elif parse_depend.index == dependent.index:
                        depend_stem = parse_depend.stem
                        depend_pos = parse_depend.pos_tag
            index_stem_map[head.index] = head_pos, head_stem
            index_stem_map[dependent.index] = depend_pos, depend_stem
        return index_stem_map

    def has_disambiguation_options(self):
        if self.is_ambiguous():
            return (self.top_parse.has_disambiguation_options() or
                    self.next_best_parse.has_disambiguation_options())
        else:
            return False

    def has_single_sided_disambiguation(self):
        if self.is_ambiguous():
            top_only = (self.top_parse.has_disambiguation_options() and
                        not self.next_best_parse.has_disambiguation_options())
            next_only = (self.next_best_parse.has_disambiguation_options() and
                         not self.top_parse.has_disambiguation_options())
            return top_only or next_only
        else:
            return False

    def has_double_sided_disambiguation(self):
        if self.is_ambiguous():
            return (self.top_parse.has_disambiguation_options() and
                    self.next_best_parse.has_disambiguation_options())
        else:
            return False

    def xmlize(self):
        attributes = {
            'text_file': self.parent_file_name,
            'sentence_id': self.full_id,
            'reference': self.reference,
            'ambiguous': str(self.is_ambiguous())}
        sentence_xml = ElementTree.Element('sentence', attributes)
        parses = [p for p in [self.top_parse, self.next_best_parse] if p]
        if self.ambiguous_span():
            ambiguous_span_xml = ElementTree.SubElement(
                sentence_xml, 'ambiguous_span')
            for head, dependent in self.ambiguous_span():
                unlabeled_attributes = {
                    'head': head,
                    'dependent': dependent}
                dependency_xml = ElementTree.Element(
                    'dependency', unlabeled_attributes)
                ambiguous_span_xml.append(dependency_xml)
        for parse in parses:
            sentence_xml.append(parse.xmlize(self.ambiguous_span()))
        return sentence_xml

