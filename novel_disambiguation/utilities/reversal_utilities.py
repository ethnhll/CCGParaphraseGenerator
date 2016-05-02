__author__ = 'Ethan A. Hill'
import string
import itertools
import logging
import re
from xml.etree import cElementTree as ElementTree
from ..models.parse import Parse
from ..models.reversal import Reversal
from disambig_utilities import sentence_utilities

__logger = logging.getLogger(__name__)


def relative_word_distances(word_index_map):
    __logger.debug('Calculating relative word distances for word mapping %s',
                   word_index_map)
    word_distances_map = {}
    for word, other_word in itertools.permutations(word_index_map.items(), 2):
        index, word = word
        other_index, other_word = other_word
        # Distances should be bi-directional
        word_distances_map[word, other_word] = index - other_index
        word_distances_map[other_word, word] = other_index - index
    __logger.debug('Calculated relative word distances as %s',
                   word_distances_map)
    return word_distances_map


def build_xpath_to_node(node, tree_parent_map):
    __logger.debug('Building up the xpath expression to a node in an xml tree.')
    # We need to gather the full xpath
    tags = []
    # 'lf' is the top level tag of a logical form
    while node is not None and node.tag != 'lf':
        # We want to ignore the id attribute to establish correspondence
        items = node.attrib
        attributes = [node.tag]
        for item in items:
            value = items[item]
            if item !='id':
                attributes.append('[@%s="%s"]' % (item, value))
        tags.append(''.join(attributes))
        node = tree_parent_map.get(node)
    # These tags are in bottom up order so we have to switch to top down
    path_to_node = '/'.join(reversed(tags))
    __logger.debug('Built xpath expression "%s" to an xml tree node.',
                   path_to_node)
    return path_to_node


def word_correspondence(parse, realization_xml, ambiguous_details_index_map):
    __logger.debug('Establishing correspondence between parse %s and its '
                   'realization.', parse)

    # Get all ambiguous words from the tree
    parse_words = parse.xml_lf.findall('.//*node[@id][@pred]')
    # Establish a mapping of child nodes to parent nodes in the tree
    child_parent_map = {c: p for p in parse.xml_lf.iter() for c in p}
    realization_lf = realization_xml.find('lf')
    # We have to assume that these word lists are the same length
    correspondence = {}
    for parse_node in parse_words:
        parse_index = parse_node.attrib.get('id')
        # prefixed with a single character
        parse_index_match = re.match('.([0-9]+).*', parse_index)
        parse_index = int(parse_index_match.group(1))
        # We are only really interested in the ambiguity for correspondence
        if parse_index in ambiguous_details_index_map:
            ambig_tag, ambig_stem = ambiguous_details_index_map[parse_index]
            parse_stem = parse_node.attrib.get('pred')
            # Stem must also match for alignment
            if ambig_stem == parse_stem:
                # Use this path to find the corresponding node in realization
                path_to_node = build_xpath_to_node(parse_node, child_parent_map)
                # Now get the realization's information
                realization_node = realization_lf.find(path_to_node)
                realization_stem = realization_node.attrib.get('pred')
                realization_index = realization_node.attrib.get('id')
                # prefixed with a single character
                realization_index_match = re.match(
                    '.([0-9]+).*', realization_index)
                realization_index = int(realization_index_match.group(1))
                correspondence[parse_index, parse_stem] = (
                    realization_index, realization_stem)
    __logger.debug('Established correspondence...%s for parse %s and its '
                   'realization.', correspondence, parse)
    return correspondence


def distances_change(reference_distances, realization_distances):
    __logger.debug('Checking for changes in distance between...%s...'
                   'and...%s', reference_distances, realization_distances)
    for words, distance in reference_distances.iteritems():
        # Default to zero in case the words don't appear in realization
        realization_distance = realization_distances.get(words, 0)
        if distance != realization_distance:
            __logger.debug('Distances changed between...%s...and...%s',
                           reference_distances, realization_distances)
            return True
    __logger.debug('Distances did not change between...%s...and...%s',
                   reference_distances, realization_distances)
    return False


def breaks_ambiguous_span(ambiguous_details_index_map, parse, realization_xml):
    __logger.debug('Checking if ambiguous span is broken by realization of '
                   'parse %s', parse)
    """
    TODO: This correspondence can probably be reduced to just the
          correspondence between the ambiguous section by finding just the
          ambiguous nodes by index, since we sort of already have those.
    """
    reference_text = parse.xml_lf.attrib.get('string')
    realization_text = realization_xml.find('str').text
    # If the text is identical, don't bother doing this other work...
    if reference_text != realization_text:
        correspondence = word_correspondence(
            parse, realization_xml, ambiguous_details_index_map)
        # Put the correspondence into separate mappings
        original_index_stem_map = {}
        realization_index_stem_map = {}
        for index, stem in correspondence:
            original_index_stem_map[index] = stem
            real_index, real_stem = correspondence[index, stem]
            realization_index_stem_map[real_index] = real_stem
        # Now get the distances from the stem maps
        original_distances = relative_word_distances(original_index_stem_map)
        realization_distances = relative_word_distances(
            realization_index_stem_map)
        return distances_change(original_distances, realization_distances)
    else:
        # The realization and reference were identical...
        __logger.debug('reference text "%s" was identical to realization text '
                       '"%s"', reference_text, realization_text)
        return False


def write_out_reversals(parse_output_directory, realizations_to_print):
    reversal_path = '%s/reversals' % parse_output_directory
    __logger.debug('Writing out %s to %s', realizations_to_print, reversal_path)
    with open(reversal_path, 'w') as reversal_file:
        # a neat trick to write out all realizations at once in one write call
        lines = '\n'.join(realizations_to_print)
        reversal_file.write(lines.encode('utf-8'))
    __logger.debug('Finisied writing out %s to %s',
                   realizations_to_print, reversal_path)
    return reversal_path


def prepare_reversals(sentences, parse_output_directory):
    __logger.debug('Preparing reversals for sentences %s using directory %s',
                   sentences, parse_output_directory)
    path_match = re.match('(^.*).dir$', parse_output_directory)
    text_file_name = path_match.group(1)
    realization_path = '%s/realize.nbest' % parse_output_directory
    realizations_xml = ElementTree.parse(realization_path)
    # Only look at the ambiguous sentences
    ambiguous = [sentence for sentence in sentences if sentence.is_ambiguous()]
    realizations_to_print = []
    for sentence in ambiguous:
        for parse in [sentence.top_parse, sentence.next_best_parse]:
            index_details_map = sentence.parse_specific_ambiguity_details(
                parse)
            realizations = realizations_xml.findall(
                './/seg[@id="%s"][@complete="true"]/*[@score]' % parse.full_id)
            # A bit long winded... builds the reversal if possible
            for realization in realizations:
                if breaks_ambiguous_span(index_details_map, parse, realization):
                    realized_text = realization.find('str').text
                    realizations_to_print.append(realized_text)
                    # Now prepare the reversal
                    reversal_sent_id = 's%d' % len(realizations_to_print)
                    parse.reversal = Reversal(
                        reversal_sent_id, text_file_name, realized_text)
                    # We've found a reversal, break out of the loop
                    break
    __logger.debug('Finished preparing reversals for sentences %s using '
                   'directory %s', sentences, parse_output_directory)
    # write out the reversals into parse_output_directory
    return write_out_reversals(parse_output_directory, realizations_to_print)


def validate_reversals(sentences, parse_output_directory):
    __logger.debug('Validating reversals for sentences %s using directory %s',
                   sentences, parse_output_directory)
    reversal_filename = '%s/reversals' % parse_output_directory
    reversal_directory_path = '%s/reversals.dir' % parse_output_directory
    reversal_lf = '%s/tb.xml' % reversal_directory_path
    reparses = Parse.parse_factory(reversal_filename, reversal_lf)
    # Now take these parses and find parses associated with each sentence
    sentence_dict = sentence_utilities.sentence_id_parse_map(reparses)
    ambiguous = [sentence for sentence in sentences if sentence.is_ambiguous()]
    for sentence in ambiguous:
        ambiguous_span = sentence.ambiguous_span()
        parses = [sentence.top_parse, sentence.next_best_parse]
        # Only look at parses which have a reversal
        parses = [parse for parse in parses if parse.reversal]
        for parse in parses:
            reversal_id = parse.reversal.reparse_sentence_id
            reversal_parses = sorted(sentence_dict.get(reversal_id))
            # Only interested in the top parse, nothing more
            top_reversal_parse = reversal_parses[0]
            parse.reversal.validate(parse, top_reversal_parse, ambiguous_span)

    __logger.debug('Finished validating reversals for sentences %s using '
                   'directory %s', sentences, parse_output_directory)