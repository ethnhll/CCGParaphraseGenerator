__author__ = 'Ethan A. Hill'
import copy
import string
import re
import itertools
import logging
from xml.etree import cElementTree as ElementTree

from ..constants import ccg_values
from ..models.rewrite import Rewrite
from ..utilities import reversal_utilities


__logger = logging.getLogger(__name__)


def find_parse_tree_node(node_index, parse):
    parse_nodes = parse.xml_lf.findall('.//node[@id]')
    for node in parse_nodes:
        parse_index = node.attrib.get('id')
        # prefixed with a single character
        parse_index_match = re.match('.([0-9]+).*', parse_index)
        if int(parse_index_match.group(1)) == node_index:
            return node
    # This should never happen
    return None


def parent_verb_node(node, parse):
    child_parent_tree_map = {c: p for p in parse.xml_lf.iter() for c in p}
    while node is not None and node.tag != 'lf':
        node = child_parent_tree_map.get(node)
        if 'id' in node.attrib:
            node_index = node.attrib.get('id')
            # prefixed with a single character
            node_index_match = re.match('.([0-9]+).*', node_index)
            node_index = int(node_index_match.group(1))
            tag = parse.pos_tag_of_word_at_index(node_index)
            if 'VB' in tag:
                return node
    # This should probably throw an exception too but maybe not
    __logger.warning('Parent verb was not found for parse %s', parse)
    return None


def has_node_as_child(node, other_node):
    other_node_index = other_node.attrib.get('id')
    if node.find('.//node[@id="%s"]' % other_node_index) is not None:
        return True
    else:
        return False


def ambiguous_parent_verb_index(node_index, parse_pair):
    parse, other_parse = parse_pair
    # Find the parent verb of the node in question from each parse
    parse_node = find_parse_tree_node(node_index, parse)
    parent_verb = parent_verb_node(parse_node, parse)
    other_parse_node = find_parse_tree_node(node_index, other_parse)
    other_parent_verb = parent_verb_node(other_parse_node, other_parse)

    # Do the parent verb nodes exist?
    if parent_verb is not None and other_parent_verb is not None:
        # Now see which verb is higher up in the tree
        if has_node_as_child(parent_verb, other_parent_verb):
            top_level_verb = parent_verb
        else:
            top_level_verb = other_parent_verb
        return top_level_verb.attrib.get('id')
    return None


def append_rewrite_to_xml_file(rewrite_xml, xml_file_path):
    xml_file = ElementTree.parse(xml_file_path)
    root = xml_file.getroot()
    root.append(rewrite_xml)
    xml_file.write(xml_file_path)


def rewrite_validation_map(parse_lf, rewrite_lf):
    verification_map = {}
    parent_child_map = {c: p for p in rewrite_lf.iter() for c in p}
    for node in parse_lf.findall('.//node[@id]'):
        node_id = node.attrib.get('id')
        # The node id's should be the same before realization
        rewrite_node = rewrite_lf.find('.//node[@id="%s"]' % node_id)
        # Use reversal utilities xpath builder...
        rewrite_path = reversal_utilities.build_xpath_to_node(
            rewrite_node, parent_child_map)
        verification_map[node_id] = rewrite_path
    return verification_map


def attempt_cleft_rewrite(verb_index, parse, xml_path):
    xml_lf_copy = copy.deepcopy(parse.xml_lf)
    # Use the copy to make the changes
    verb_node = xml_lf_copy.find('.//node[@id="%s"]' % verb_index)
    subject_node = verb_node.find('rel[@name="Arg0"]/node[@id]')
    object_node = verb_node.find('rel[@name="Arg1"]/node[@id]')

    # If these nodes don't exist, then we can't apply this rewrite
    if subject_node is not None and object_node is not None:
        xml_lf_copy.attrib['info'] += '#cleft'
        verb_parent = xml_lf_copy.find('.//node[@id="%s"]/..' % verb_index)
        # Create a be verb above the verb parent
        be_node = ElementTree.SubElement(
            verb_parent, 'node', {'id': 'w0b', 'pred': 'be'})
        # Gather attributes from verb and transplant into be node
        for attribute, val in verb_node.items():
            if attribute not in ['id', 'pred']:
                be_node.attrib[attribute] = val
        if 'mood' in verb_node.attrib:
            verb_node.attrib.pop('mood')

        # Find the object under the verb
        object_parent = verb_node.find("./rel[@name='Arg1']/node/..")
        # Add object to 'be' verb, and remove object from verb
        object_parent_be = ElementTree.SubElement(
            be_node, 'rel', {'name': 'Arg0'})
        object_parent_be.append(object_node)
        verb_node.remove(object_parent)

        # Create long arg chain for verb node to fall under
        be_verb_child = ElementTree.SubElement(
            be_node, 'rel', {'name': 'Arg1'})
        x1_node = ElementTree.SubElement(
            be_verb_child, 'node', {'id': 'x1'})
        gen_rel = ElementTree.SubElement(
            x1_node, 'rel', {'name': 'GenRel'})
        gen_rel.append(verb_node)
        # Append an x2 node to the verb
        verb_node_child = ElementTree.SubElement(
            verb_node, 'rel', {'name': 'Arg1'})
        ElementTree.SubElement(verb_node_child, 'node', {'idref': 'x2'})
        # Remove verb from old parent
        verb_parent.remove(verb_node)

        # Append the newly created tree to the list of parse lfs
        append_rewrite_to_xml_file(xml_lf_copy, xml_path)
        # Add the rewrite to the parse
        rewrite_id = xml_lf_copy.attrib.get('info')
        validation_map = rewrite_validation_map(parse.xml_lf, xml_lf_copy)
        parse.rewrites.append(Rewrite(rewrite_id, validation_map))


def attempt_passive_rewrite(verb_index, parse, xml_path):
    xml_lf_copy = copy.deepcopy(parse.xml_lf)
    # Use the copy to make the changes
    verb_node = xml_lf_copy.find('.//node[@id="%s"]' % verb_index)
    subject_node = verb_node.find('rel[@name="Arg0"]/node[@id]')
    object_node = verb_node.find('rel[@name="Arg1"]/node[@id]')

    # If these nodes don't exist, then we can't apply this rewrite
    if subject_node is not None and object_node is not None:
        # Create a copy of this node and set up its attributes
        xml_lf_copy.attrib['info'] += '#passive'

        verb_parent = xml_lf_copy.find('.//node[@id="%s"]/..' % verb_index)
        passive_node = ElementTree.SubElement(
            verb_parent, 'node', {'id': 'w0pass', 'pred': 'PASS'})

        # Gather attributes from verb and transplant into passive node
        for attribute, value in verb_node.items():
            if attribute not in ['id', 'pred']:
                verb_node.attrib.pop(attribute)
                passive_node.attrib[attribute] = value
                verb_node.attrib['partic'] = 'pass'
        # Move the object node from the verb node to the passive node
        object_parent = verb_node.find('rel[@name="Arg1"]/node/..')

        object_parent.set('name', 'Arg0')
        passive_node.append(object_parent)
        verb_node.remove(object_parent)
        # Add a reference to the object to the parent
        object_reference_parent = ElementTree.SubElement(
            verb_node, 'rel', {'name': 'Arg1'})

        object_reference_id = object_node.attrib.get(
            'id', object_node.attrib.get('idref'))

        ElementTree.SubElement(
            object_reference_parent, 'node', {'idref': object_reference_id})
        # Create a 'by' node
        by_node_parent = ElementTree.SubElement(
            verb_node, 'rel', {'name': 'Arg0'})

        by_node = ElementTree.SubElement(
            by_node_parent, 'node', {'id': 'w0by', 'pred': 'by'})
        # Move the subject over to the passive node, under the by node
        subject_parent = verb_node.find('rel[@name="Arg0"]/node/..')

        subject_parent.set('name', 'Arg1')
        # Change the subject pred if it is a pronoun
        if subject_node.attrib.get('pred') in ccg_values.OBJECT_PRONOUNS:
            pronoun_to_change = subject_node.attrib.get('pred')
            new_pronoun = ccg_values.OBJECT_PRONOUNS.get(pronoun_to_change)
            subject_node.set('pred', new_pronoun)
        by_node.append(subject_parent)
        verb_node.remove(subject_parent)
        # Append completed verb node to passive node
        new_verb_parent = ElementTree.SubElement(
            passive_node, 'rel', {'name': 'Arg1'})

        new_verb_parent.append(verb_node)
        verb_parent.remove(verb_node)

        # Append the newly created tree to the list of parse lfs
        append_rewrite_to_xml_file(xml_lf_copy, xml_path)
        # Add the rewrite to the parse
        rewrite_id = xml_lf_copy.attrib.get('info')
        validation_map = rewrite_validation_map(parse.xml_lf, xml_lf_copy)
        parse.rewrites.append(Rewrite(rewrite_id, validation_map))


def attempt_coordination_rewrite(conjunction_index, parse, xml_path):
    conjunction_node = find_parse_tree_node(conjunction_index, parse)
    conjunction_node_index = conjunction_node.attrib.get('id')

    xml_lf_copy = copy.deepcopy(parse.xml_lf)
    # Refind this node with the xml copy
    conjunction_node = xml_lf_copy.find(
        './/node[@id="%s"]' % conjunction_node_index)
    first_node = conjunction_node.find('rel[@name="First"]/node[@id]')
    next_node = conjunction_node.find('rel[@name="Next"]/node[@id]')

    if first_node is not None and next_node is not None:
        xml_lf_copy.attrib['info'] += '#coordination'
        # Transplant the nodes on the conjunction to first and next nodes
        nodes_on_conjunction = []
        for node in conjunction_node:
            is_first = 'First' in node.attrib.values()
            is_next = 'Next' in node.attrib.values()
            if not is_first and not is_next:
                conjunction_node.remove(node)
                nodes_on_conjunction.append(node)
        # When we transplant the nodes, make sure the ids are not the same
        existing_ids = set()
        for i, node in enumerate([first_node, next_node]):
            for transplant in nodes_on_conjunction:
                copy_transplant = copy.deepcopy(transplant)
                # Alter sub elements of transplant to avoid reference issues
                for sub in copy_transplant.iter():
                    if sub.attrib.get('id'):
                        sub_id = sub.attrib.get('id')
                        # Change the id a little if already used before
                        if sub_id in existing_ids:
                            sub_id = '%scoord%d' % (sub_id, i)
                        existing_ids.add(sub_id)
                        sub.set('id', sub_id)
                node.append(copy_transplant)
        # Now switch first node with next node
        first_node_parent = conjunction_node.find(
            'rel[@name="First"]/node[@id]/..')

        next_node_parent = conjunction_node.find(
            'rel[@name="Next"]/node[@id]/..')
        first_node_parent.set('name', 'Next')
        next_node_parent.set('name', 'First')
        # Append the newly created tree to the list of parse lfs
        append_rewrite_to_xml_file(xml_lf_copy, xml_path)
        # Add the rewrite to the parse
        rewrite_id = xml_lf_copy.attrib.get('info')
        validation_map = rewrite_validation_map(parse.xml_lf, xml_lf_copy)
        parse.rewrites.append(Rewrite(rewrite_id, validation_map))


def attempt_rewrites(parse_pair, parse_specific_ambiguity_details, xml_path):
    parse, other_parse = parse_pair
    for index, details in parse_specific_ambiguity_details.iteritems():
        pos_tag, stem = details
        if 'RB' in pos_tag or 'IN' in pos_tag:
            verb_index = ambiguous_parent_verb_index(index, parse_pair)
            # If finding the parent verb index was successful
            if verb_index:
                attempt_passive_rewrite(verb_index, parse, xml_path)
                attempt_cleft_rewrite(verb_index, parse, xml_path)
            break
        elif 'CC' in pos_tag:
            attempt_coordination_rewrite(index, parse, xml_path)
            break


def apply_rewrites(sentences, parse_output_directory):
    __logger.debug('Applying possible rewrites to sentences %s', sentences)
    xml_path = '%s/tb.xml' % parse_output_directory
    ambiguous = [sentence for sentence in sentences if sentence.is_ambiguous()]
    for sentence in ambiguous:
        parses = [sentence.top_parse, sentence.next_best_parse]
        # Iterate over (top, next best) and then (next best, top)
        for ordered_parse_pair in itertools.permutations(parses, 2):
            parse, other_parse = ordered_parse_pair
            ambiguity_details = sentence.parse_specific_ambiguity_details(parse)
            attempt_rewrites(
                ordered_parse_pair, ambiguity_details, xml_path)
    __logger.debug('Finished applying possible rewrites to sentences %s',
                   sentences)


def rewrite_word_correspondence(parse, realization_xml, rewrite, ambiguity):
    __logger.debug('Establishing correspondence between parse %s and its '
                   'realization.', parse)
    realization_lf = realization_xml.find('lf')
    # We have to assume that these word lists are the same length
    correspondence = {}
    for parse_node_index, path_to_node in rewrite.validation_map.iteritems():
        # Gather parse details
        parse_node = parse.xml_lf.find('.//node[@id="%s"]' % parse_node_index)
        # prefixed with a single character
        parse_index_match = re.match('.([0-9]+).*', parse_node_index)
        parse_index = int(parse_index_match.group(1))
        # We are only interested in the ambiguity
        if parse_index in ambiguity:
            parse_stem = parse_node.attrib.get('pred')
            ambig_tag, ambig_stem = ambiguity[parse_index]
            # For alignment, stems must match too
            if parse_stem == ambig_stem:
                # Gather rewrite details
                realization_word = realization_lf.find(path_to_node)
                realization_stem = realization_word.attrib.get('pred')
                realization_index = realization_word.attrib.get('id')
                # prefixed with a single character
                realization_index_match = re.match(
                    '.([0-9]+).*', realization_index)
                realization_index = int(realization_index_match.group(1))
                correspondence[parse_index, parse_stem] = (
                    realization_index, realization_stem)
    __logger.debug('Established correspondence...\n%s \nfor parse %s and its '
                   'realization.', correspondence, parse)
    return correspondence


def breaks_ambiguous_span(ambiguous_details_map, parse, realization, rewrite):
    __logger.debug('Checking if realization %s for rewrite %s breaks ambiguous '
                   'span for parse %s', realization, rewrite, parse)

    reference_text = parse.xml_lf.attrib.get('string')
    realization_text = realization.find('str').text
    # If the text is identical, don't bother doing this other work...
    if reference_text != realization_text:
        correspondence = rewrite_word_correspondence(
            parse, realization, rewrite, ambiguous_details_map)
        # Put the correspondence into separate mappings
        original_index_stem_map = {}
        realization_index_stem_map = {}
        for index, stem in correspondence:
            original_index_stem_map[index] = stem
            real_index, real_stem = correspondence[index, stem]
            realization_index_stem_map[real_index] = real_stem

        # Now get the distances from the stem maps using a reversal utility
        original_distances = reversal_utilities.relative_word_distances(
            original_index_stem_map)
        realization_distances = reversal_utilities.relative_word_distances(
            realization_index_stem_map)
        # Check if the distances have changed
        span_is_broken = reversal_utilities.distances_change(
            original_distances, realization_distances)
        if span_is_broken:
            __logger.debug('Realization %s breaks ambiguous span for parse %s',
                           realization, parse)
        else:
            __logger.debug('Realization %s does not break ambiguous span '
                           'for parse %s', realization, parse)
        return span_is_broken
    else:
        # Realization and reference text were the same which should not happen
        __logger.warning('Rewrite realization "%s" was the same as reference '
                         '"%s"', realization_text, reference_text)
        return False


def validate_rewrites(sentences, parse_output_directory):
    realization_path = '%s/realize.nbest' % parse_output_directory
    realizations_xml = ElementTree.parse(realization_path)
    ambiguous = [sentence for sentence in sentences if sentence.is_ambiguous()]
    for sentence in ambiguous:
        for parse in [sentence.top_parse, sentence.next_best_parse]:
            details_map = sentence.parse_specific_ambiguity_details(
                parse)
            # We don't really want to look at coordination rewrites
            for rewrite in parse.rewrites:
                realizations = realizations_xml.findall(
                    './/seg[@id="%s"][@complete="true"]/*[@score]' %
                    rewrite.full_id)
                for real in realizations:
                    if breaks_ambiguous_span(details_map, parse, real, rewrite):
                        realized_text = real.find('str').text
                        # We've found a realization, break out of the loop
                        rewrite.realization = realized_text
                        rewrite.is_valid = True
                        break
                else:
                    rewrite.realization = ''
                    rewrite.is_valid = False