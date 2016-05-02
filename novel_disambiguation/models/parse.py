__author__ = 'Ethan A. Hill'
import re
import collections
from xml.etree import cElementTree as ElementTree

WordInfo = collections.namedtuple(
    'WordInfo', ['word', 'index', 'pos_tag', 'stem'])
UnlabeledDependency = collections.namedtuple(
    'UnlabeledDependency', ['head', 'dependent'])


class Parse:
    __REFERENCE = 'string'
    __FULL_WORDS = 'full-words'
    __PRED_INFO = 'pred-info'

    def __init__(self, parent_filename, xml_lf):
        self.xml_lf = xml_lf
        self.filename = str(parent_filename.encode('utf8'))
        self.full_id = self.xml_lf.attrib['info']
        self.text = str(self.xml_lf.attrib['string'].encode('utf8'))
        self.dependency_details_map = self.__get_dependencies_from_lf(xml_lf)
        self.reversal = None
        self.rewrites = []
        self.__word_info_map = self.__get_word_info_map(xml_lf)

    def __str__(self):
        rep = 'Parse(parent_filename: {!s}, full_id: {!s}, text: {!s})'.format(
            self.filename,
            self.full_id,
            self.text)
        return rep

    def __repr__(self):
        rep = 'Parse(parent_filename: {!s}, full_id: {!s}, text: {!s})'.format(
            self.filename,
            self.full_id,
            self.text)
        return rep

    def __cmp__(self, other):
        sentence_id, parse_number = self.full_id.split('-')
        other_sentence_id, other_parse_number = other.full_id.split('-')

        sentence_number = int(sentence_id[1:])
        other_sentence_number = int(other_sentence_id[1:])
        if sentence_number == other_sentence_number:
            parse_number = int(parse_number)
            other_parse_number = int(other_parse_number)
            return cmp(parse_number, other_parse_number)
        else:
            return cmp(sentence_number, other_sentence_number)

    def __eq__(self, other):
        return (self.full_id == other.full_id and
                self.dependency_detail_set() == other.dependency_detail_set())

    def __ne__(self, other):
        return (self.full_id != other.full_id or
                self.dependency_detail_set() != other.dependency_detail_set())

    def __lt__(self, other):
        sentence_id, parse_number = self.full_id.split('-')
        other_sentence_id, other_parse_number = other.full_id.split('-')

        sentence_number = int(sentence_id[1:])
        other_sentence_number = int(other_sentence_id[1:])
        if sentence_number == other_sentence_number:
            parse_number = int(parse_number)
            other_parse_number = int(other_parse_number)
            return parse_number < other_parse_number
        else:
            return sentence_number < other_sentence_number

    def __gt__(self, other):
        sentence_id, parse_number = self.full_id.split('-')
        other_sentence_id, other_parse_number = other.full_id.split('-')

        sentence_number = int(sentence_id[1:])
        other_sentence_number = int(other_sentence_id[1:])
        if sentence_number == other_sentence_number:
            parse_number = int(parse_number)
            other_parse_number = int(other_parse_number)
            return parse_number > other_parse_number
        else:
            return sentence_number > other_sentence_number

    def __le__(self, other):
        sentence_id, parse_number = self.full_id.split('-')
        other_sentence_id, other_parse_number = other.full_id.split('-')

        sentence_number = int(sentence_id[1:])
        other_sentence_number = int(other_sentence_id[1:])
        if sentence_number == other_sentence_number:
            parse_number = int(parse_number)
            other_parse_number = int(other_parse_number)
            return parse_number <= other_parse_number
        else:
            return sentence_number <= other_sentence_number

    def __ge__(self, other):
        sentence_id, parse_number = self.full_id.split('-')
        other_sentence_id, other_parse_number = other.full_id.split('-')

        sentence_number = int(sentence_id[1:])
        other_sentence_number = int(other_sentence_id[1:])
        if sentence_number == other_sentence_number:
            parse_number = int(parse_number)
            other_parse_number = int(other_parse_number)
            return parse_number >= other_parse_number
        else:
            return sentence_number >= other_sentence_number

    def unlabeled_dependency_set(self):
        return set(self.dependency_details_map.values())

    def dependency_detail_set(self):
        return set(self.dependency_details_map.keys())

    def sentence_id(self):
        sentence_id, parse_number = self.full_id.split('-')
        return sentence_id

    def reference_sentence(self):
        return self.xml_lf.attrib.get(self.__REFERENCE, '')

    @staticmethod
    def __get_word_info_map(lf):
        full_words_text = lf.find(Parse.__FULL_WORDS).text
        word_info_map = Parse.__get_info_word_tag_index(full_words_text)

        pred_info_node = lf.find(Parse.__PRED_INFO)
        pred_info_text = pred_info_node.attrib.get('data')
        word_stem_map = Parse.__get_word_stem(pred_info_text)
        word_info_map = Parse.__combine_info_and_stem_map(
            word_info_map, word_stem_map)
        return word_info_map

    @staticmethod
    def __get_dependencies_from_lf(lf):
        word_info_map = Parse.__get_word_info_map(lf)
        dependency_details = {}
        # Find all nodes which have a 'rel' child
        for sub_element in lf.findall('.//node/rel/..'):
            # Update the dictionary as we go along
            sub_map = Parse.__get_dependency_details(sub_element, word_info_map)
            dependency_details.update(sub_map)
        return dependency_details

    @staticmethod
    def __get_word_stem(pred_info):
        word_stem_map = {}
        pred_info_split = pred_info.split()
        for info in pred_info_split:
            match = re.match('^.([0-9]+).*:.*:.*:(.*)$', info)
            index = int(match.group(1))
            word_stem = match.group(2)
            word_stem = Parse.__restore_subbed_tokens(word_stem)
            word_stem_map[index] = word_stem
        return word_stem_map

    @staticmethod
    def __restore_subbed_tokens(tokenized):
        tokenized = re.sub(r'&apos;', "'", tokenized)
        tokenized = re.sub(r'&quot;', '"', tokenized)
        tokenized = re.sub(r'&#45;', '-', tokenized)
        tokenized = re.sub(r'&#58;', ':', tokenized)
        tokenized = re.sub(r'&amp;', '&', tokenized)
        tokenized = re.sub(r'&#45;', '-', tokenized)
        tokenized = re.sub(r'&lt;', '<', tokenized)
        tokenized = re.sub(r'&gt;', '>', tokenized)
        tokenized = re.sub(r'\\/', '/', tokenized)
        return tokenized

    @staticmethod
    def __get_info_word_tag_index(full_words):
        info_list = full_words.split()
        # We don't want to look at the ending markers
        info_list = info_list[1:-1]
        word_info_map = {}
        for index, info in enumerate(info_list, start=1):
            # Here our match groups will grab the info we need
            matches = re.match('(^.*):S-.*:P-(.*):T-', info)
            if matches:
                # Fix the substitutions
                word = Parse.__restore_subbed_tokens(matches.group(1))
                pos_tag = matches.group(2)
                word_info = WordInfo(word, index, pos_tag, '')
                word_info_map[index - 1] = word_info
        return word_info_map

    @staticmethod
    def __combine_info_and_stem_map(word_info_map, index_stem_map):
        # Now add the stems to the word_info_map
        for index, stem in index_stem_map.iteritems():
            word_info = word_info_map[index]
            # Named tuples are immutable unfortunately so we must reassign
            word_info = WordInfo(
                word_info.word, index, word_info.pos_tag, stem)
            word_info_map[index] = word_info
        return word_info_map

    @staticmethod
    def __get_dependency_details(node, word_info_map):
        # Some nested trickery with dict's get method
        head_id = node.attrib.get('id', node.attrib.get('idref'))
        match = re.match('.([0-9]+).*', head_id)
        head_index = int(match.group(1))

        head_details = word_info_map[head_index]
        dependency_map = {}
        # Examine all nodes whose parent is 'rel'
        for sub_node in node.findall('rel/*'):
            dependent_id = sub_node.attrib.get(
                'id', sub_node.attrib.get('idref'))
            match = re.match('.([0-9]+).*', dependent_id)
            dependent_index = int(match.group(1))

            dependent_details = word_info_map[dependent_index]
            dependency = UnlabeledDependency(
                head_details.word, dependent_details.word)
            dependency_map[head_details, dependent_details] = dependency
        return dependency_map

    @staticmethod
    def parse_factory(parent_filename, logical_form_file):
        parse_tree = ElementTree.parse(logical_form_file)
        lfs = parse_tree.findall('.//item')
        # Ignore items with no parse lfs
        lfs = [lf for lf in lfs if int(lf.attrib.get('numOfParses')) > 0]
        # Don't create parses for rewrite lfs
        return [Parse(parent_filename, lf) for lf in lfs if '#' not in lf.attrib.get('info')]

    def has_valid_reversal(self):
        # is_validated can return None if the reversal was not yet checked
        if self.reversal and self.reversal.is_validated():
            return True
        else:
            return False

    def pos_tag_of_word_at_index(self, word_index):
        if word_index in self.__word_info_map:
            info = self.__word_info_map.get(word_index)
            return info.pos_tag
        else:
            # TODO:Probably should throw an exception here
            return None

    def stem_of_word_at_index(self, word_index):
        if word_index in self.__word_info_map:
            info = self.__word_info_map.get(word_index)
            return info.stem
        else:
            # TODO:Probably should throw an exception here
            return None

    def has_valid_rewrites(self):
        for rewrite in self.rewrites:
            if rewrite.is_valid:
                return True
        return False

    def has_disambiguation_options(self):
        return self.has_valid_reversal() or self.has_valid_rewrites()

    def xmlize(self, ambiguous_span):
        attributes = {'id': self.full_id, }
        parse_xml = ElementTree.Element('parse', attributes)
        info_xml = ElementTree.SubElement(parse_xml, 'dependencies')
        for info, unlabeled in self.dependency_details_map.iteritems():
            head, dependent = info
            # These are namedtuples, _asdict is public but gives OrderedDict
            head_dict = dict(head._asdict())
            dependent_dict = dict(dependent._asdict())
            info_attributes = {
                'head': str(head_dict),
                'dependent': str(dependent_dict),
                'ambiguous': str(unlabeled in ambiguous_span)}
            ElementTree.SubElement(info_xml, 'dependency', info_attributes)
        if self.reversal:
            parse_xml.append(self.reversal.xmlize())
        for rewrite in self.rewrites:
            parse_xml.append(rewrite.xmlize())
        return parse_xml