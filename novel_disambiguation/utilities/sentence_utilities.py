__author__ = 'Ethan A. Hill'
import re
import logging
from collections import defaultdict
from ..constants import ccg_values
from ..models.parse import Parse
from ..models.sentence import Sentence

__logger = logging.getLogger(__name__)


def has_dependency_self_reference(parse):
    unlabeled_dependencies = parse.unlabeled_dependency_set()
    # If head == dependent, we want to filter this parse out
    has_self_reference = any(head == dependent for head, dependent in unlabeled_dependencies)
    if has_self_reference:
        __logger.debug("Parse [{!s}] has dependency where head is the same as dependent".format(parse))
    return has_self_reference


def has_single_root(parse):
    # Examine the internal xml of the parse
    lf_roots = parse.xml_lf.findall('lf/*')
    num_roots = len(lf_roots)
    if num_roots != 1:
        __logger.debug("Parse [{!s}] has {!s} roots".format(parse, num_roots))
    return num_roots == 1


def should_apply_filter(parse):
    apply_filter = has_dependency_self_reference(parse) or not has_single_root(parse)
    if apply_filter:
        __logger.debug("Parse [{!s}] should be filtered".format(parse))
    return apply_filter


def different_by_reverse_dependency_only(parse, other):
    dependencies = parse.unlabeled_dependency_set()
    other_dependencies = other.unlabeled_dependency_set()
    difference = dependencies.symmetric_difference(other_dependencies)
    # We are looking only at a difference where one parse has (head, dependent)
    # and the other has (dependent, head)
    if len(difference) == 2:
        head, dependent = difference.pop()
        if (dependent, head) in difference:
            __logger.debug("Parse [{!s}] and [{!s}] are different only by "
                           "a dependency's direction being reversed".format(parse, other))
            return True
    return False


def different_by_one_dependency_only(parse, other):
    dependencies = parse.unlabeled_dependency_set()
    other_dependencies = other.unlabeled_dependency_set()
    difference = dependencies.symmetric_difference(other_dependencies)
    if len(difference) == 1:
        __logger.debug("Parse [{!s}] and [{!s}] are different only by a "
                       "single extra dependency arc".format(parse, other))
        return True
    else:
        return False


def has_auxiliary_attachment(parse, attachment_details):
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
    if head_tag_match:
        __logger.debug("Parse [{!s}] has head with aux tag from list {!s}".format(parse, ccg_values.HEAD_AUX_TAGS))
    head_word_match = any(head_word in verbs for verbs in aux_verbs)
    if head_word_match:
        __logger.debug("Parse [{!s}] has head with an aux verb from list {!s}".format(parse, aux_verbs))
    head_match = head_tag_match or head_word_match
    # dependent only needs to involve the tags
    depend_match = any(depend_tag in t for t in ccg_values.DEPENDENT_AUX_TAGS)
    if depend_match:
        __logger.debug("Parse [{!s}] has dependent with an aux tag from list {!s}".format(parse, ccg_values.DEPENDENT_AUX_TAGS))
    has_aux = head_match and depend_match
    if has_aux:
        __logger.debug("Parse [{!s}] has an auxiliary attachment".format(parse))
    return has_aux


def has_uninteresting_dependency_difference(parse, other):
    dependencies = parse.unlabeled_dependency_set()
    other_dependencies = other.unlabeled_dependency_set()
    differences = dependencies.symmetric_difference(other_dependencies)
    for examine in [parse, other]:
        dependencies = examine.dependency_details_map
        for details, unlabeled in dependencies.iteritems():
            # We only want to look at the details of the ambiguous span
            if unlabeled in differences and has_auxiliary_attachment(examine, details):
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
    __logger.debug("Parse [{!s}] and [{!s}] do not have different enough dependencies".format(parse, other))
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
    parses = Parse.parse_factory(text_file_name, lf_path)
    # Now examine these Parses and filter out those which have a
    # self-reference (ie. head == dependent) and which have two roots..
    parses = [parse for parse in parses if not should_apply_filter(parse)]
    sentence_dict = sentence_id_parse_map(parses)
    # Now generate the sentences...
    sentences = []
    for sentence_id, sent_parses in sentence_dict.iteritems():
        # Grab the top two parses (next_best may be None)
        top_parse, next_best_parse = gather_both_top_parses(sent_parses)
        if next_best_parse is None:
            __logger.debug("Next best parse not found for sentence: {!s}, file:{!s}".format(sentence_id, text_file_name))
        sentences.append(Sentence(text_file_name, top_parse, next_best_parse))
    return sentences
