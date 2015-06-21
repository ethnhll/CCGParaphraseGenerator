__author__ = 'Ethan A. Hill'
import re
from collections import defaultdict
from ..constants import ccg_values
from ..models.parse import Parse
from ..models.sentence import Sentence


def has_dependency_self_reference(parse):
    unlabeled_dependencies = parse.unlabeled_dependency_set()
    # If head == dependent, we want to filter this parse out
    return any(head == dependent for head, dependent in unlabeled_dependencies)


def has_single_root(parse):
    # Examine the internal xml of the parse
    lf_roots = parse.xml_lf.findall('lf/*')
    return len(lf_roots) == 1


def should_apply_filter(parse):
    return has_dependency_self_reference(parse) or not has_single_root(parse)


def different_by_reverse_dependency_only(parse, other):
    dependencies = parse.unlabeled_dependency_set()
    other_dependencies = other.unlabeled_dependency_set()
    difference = dependencies.symmetric_difference(other_dependencies)
    # We are looking only at a difference where one parse has (head, dependent)
    # and the other has (dependent, head)
    if len(difference) == 2:
        head, dependent = difference.pop()
        if (dependent, head) in difference:
            return True
    return False


def different_by_one_dependency_only(parse, other):
    dependencies = parse.unlabeled_dependency_set()
    other_dependencies = other.unlabeled_dependency_set()
    difference = dependencies.symmetric_difference(other_dependencies)
    return True if len(difference) == 1 else False


def has_auxiliary_attachment(attachment_details):
    # Gather up all aux verb forms from constants
    aux_verbs = (ccg_values.BE_VERB_FORMS + ccg_values.HAVE_VERB_FORMS +
                 ccg_values.DO_VERB_FORMS)
    # Look at cases of (head=aux verbs or MD tag, dependent=JJ/IN/RB)
    head_details, dependent_details = attachment_details
    # Lowering the word just because all the constants are lowered
    head_word, head_tag = head_details.word.lower(), head_details.pos_tag
    depend_tag = dependent_details.pos_tag
    # Iterate over the tags we've defined in our constants as aux
    head_tag_match = any(head_tag in tag for tag in ccg_values.HEAD_AUX_TAGS)
    head_word_match = any(head_word in verbs for verbs in aux_verbs)
    head_match = head_tag_match or head_word_match
    # dependent only needs to involve the tags
    depend_match = any(depend_tag in t for t in ccg_values.DEPENDENT_AUX_TAGS)
    return head_match and depend_match


def has_uninteresting_dependency_difference(parse, other):
    dependencies = parse.unlabeled_dependency_set()
    other_dependencies = other.unlabeled_dependency_set()
    differences = dependencies.symmetric_difference(other_dependencies)
    for examine in [parse, other]:
        dependencies = examine.dependency_details_map
        for details, unlabeled in dependencies.iteritems():
            # We only want to look at the details of the ambiguous span
            if unlabeled in differences and has_auxiliary_attachment(details):
                return True
    return False


def is_different_enough(parse, other):
    if parse.unlabeled_dependency_set() != other.unlabeled_dependency_set():
        # Gather up all the conditions that we are filtering on
        only_by_reverse = different_by_reverse_dependency_only(parse, other)
        only_by_one = different_by_one_dependency_only(parse, other)
        bad_attachment = has_uninteresting_dependency_difference(parse, other)
        if not only_by_reverse and not only_by_one and not bad_attachment:
            return True
    return False


def gather_both_top_parses(parses):
    top_parse = None
    for parse in sorted(parses):
        if top_parse is None:
            top_parse = parse
        elif is_different_enough(top_parse, parse):
            return top_parse, parse
    return top_parse, None


def sentence_id_parse_map(parses):
    sentence_dict = defaultdict(list)
    for parse in parses:
        sentence_id = parse.sentence_id()
        sentence_dict[sentence_id] += [parse]
    return sentence_dict


def sentence_factory(parse_output_directory):
    lf_path = '%s/tb.xml' % parse_output_directory
    # Extract the sentence filename from the parse directory
    path_match = re.match('(^.*).dir$', parse_output_directory)
    text_file_name = path_match.group(1)
    # Gather all parses
    parses = Parse.parse_factory(lf_path)
    # Now examine these Parses and filter out those which have a
    # self-reference (ie. head == dependent) and which have two roots..
    parses = [parse for parse in parses if not should_apply_filter(parse)]
    sentence_dict = sentence_id_parse_map(parses)
    # Now generate the sentences...
    sentences = []
    for sentence_id, sent_parses in sentence_dict.iteritems():
        # Grab the top two parses (next_best may be None)
        top_parse, next_best_parse = gather_both_top_parses(sent_parses)
        sentences.append(Sentence(text_file_name, top_parse, next_best_parse))
    return sentences