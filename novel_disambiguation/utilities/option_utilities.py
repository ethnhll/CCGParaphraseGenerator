import itertools
from xml.etree import cElementTree as ElementTree
from ..models.disambiguation_option import DisambiguationOption
from ..models.disambiguation import Disambiguation


def options_factory(sentence):
    options = []
    if sentence.is_ambiguous():
        if sentence.has_double_sided_disambiguation():
            two_sided = two_sided_options(sentence)
            options.extend(two_sided)
        elif sentence.has_single_sided_disambiguation():
            one_sided = one_sided_options(sentence)
            options.extend(one_sided)
    return options


def write_out_dump(options, xml_dump_path):
    xml_root = ElementTree.Element('novel_disambiguation')
    for option in options:
        xml_root.append(option.xmlize())
    xml_tree = ElementTree.ElementTree(xml_root)
    xml_tree.write(xml_dump_path, encoding='utf-8')


def two_sided_options(sentence):
    options = []
    top, next_best = sentence.top_parse, sentence.next_best_parse
    # Has two reversals, though only one option will be added
    if top.has_valid_reversal() and next_best.has_valid_reversal():
        option = two_sided_reversal(sentence)
        options.append(option)
    # Has two-sided rewrites
    if top.has_valid_rewrites() and next_best.has_valid_rewrites():
        rewrites = two_sided_rewrites(sentence)
        # Possibly more than one option will get added
        options.extend(rewrites)

    # # Gather up conditions for special cases
    # top_reversal_combines = (top.has_valid_reversal() and
    #                          not top.has_valid_rewrites() and
    #                          not next_best.has_valid_reversal() and
    #                          next_best.has_valid_rewrites())
    # next_reversal_combines = (next_best.has_valid_reversal() and
    #                           not next_best.has_valid_rewrites() and
    #                           not top.has_valid_reversal() and
    #                           top.has_valid_rewrites())
    # # Combine the reversals and rewrites for special cases
    # if top_reversal_combines:
    #     combined = combine_reversals_and_rewrites(
    #         sentence, top, next_best)
    #     # Add the combinations all at once
    #     options.extend(combined)
    # elif next_reversal_combines:
    #     combined = combine_reversals_and_rewrites(
    #         sentence, next_best, top)
    #     # Add the combinations all at once
    #     options.extend(combined)
    return options


def one_sided_options(sentence):
    if sentence.top_parse.has_disambiguation_options():
        parse = sentence.top_parse
        other_parse = sentence.next_best_parse
    else:
        parse = sentence.next_best_parse
        other_parse = sentence.top_parse

    options = []
    if parse.has_valid_reversal():
        # Create the option
        reversal = DisambiguationOption(sentence)
        realization = parse.reversal.realization
        disambig = Disambiguation(parse.full_id,
                                  DisambiguationOption.REVERSAL,
                                  realization,
                                  parse.dependency_details_map)
        other_disambig = Disambiguation(other_parse.full_id, '', '',
                                        other_parse.dependency_details_map)
        reversal.disambiguations.extend([disambig, other_disambig])
        # Add the reversal to the list of options
        options.append(reversal)
    if parse.has_valid_rewrites():
        # Create options for each rewrite
        valid_rewrites = [r for r in parse.rewrites if r.is_valid]
        for rewrite in valid_rewrites:
            # Create the option
            rewrite_opt = DisambiguationOption(sentence)
            disambig = Disambiguation(rewrite.parse_id(),
                                      rewrite.type_of_change(),
                                      rewrite.realization,
                                      parse.dependency_details_map)
            other_disambig = Disambiguation(other_parse.full_id, '', '',
                                            other_parse.dependency_details_map)
            rewrite_opt.disambiguations.extend([disambig, other_disambig])
            options.append(rewrite_opt)
    return options


def two_sided_reversal(sentence):
    # Creates one option but adds both reversal realizations to the option
    option = DisambiguationOption(sentence)
    parses = [sentence.top_parse, sentence.next_best_parse]
    for parse in parses:
        realization = parse.reversal.realization
        disambig = Disambiguation(parse.full_id,
                                  DisambiguationOption.REVERSAL,
                                  realization,
                                  parse.dependency_details_map)
        option.disambiguations.append(disambig)
    return option


def combine_two_sided_rewrites(sentence):
    # Here we combine rewrites which do not have matches of type
    top, next_best = sentence.top_parse, sentence.next_best_parse
    tops_rewrites = [r for r in top.rewrites if r.is_valid]
    next_bests_rewrites = [r for r in next_best.rewrites if r.is_valid]
    options = []
    combinations = itertools.product(tops_rewrites, next_bests_rewrites)
    for rewrite, other_rewrite in combinations:
        option = DisambiguationOption(sentence)
        disambig = Disambiguation(rewrite.parse_id(),
                                  rewrite.type_of_change(),
                                  rewrite.realization,
                                  top.dependency_details_map)
        other_dis = Disambiguation(other_rewrite.parse_id(),
                                   other_rewrite.type_of_change(),
                                   other_rewrite.realization,
                                   next_best.dependency_details_map)
        option.disambiguations.extend([disambig, other_dis])
        options.append(option)
    return options


def two_sided_rewrites(sentence):
    top, next_best = sentence.top_parse, sentence.next_best_parse
    tops_rewrites = [r for r in top.rewrites if r.is_valid]
    next_bests_rewrites = [r for r in next_best.rewrites if r.is_valid]
    options = []
    combinations = itertools.product(tops_rewrites, next_bests_rewrites)
    for rewrite, other_rewrite in combinations:
        if rewrite.type_of_change() == other_rewrite.type_of_change():
            option = DisambiguationOption(sentence)
            disambig = Disambiguation(rewrite.parse_id(),
                                      rewrite.type_of_change(),
                                      rewrite.realization,
                                      top.dependency_details_map)
            other_dis = Disambiguation(other_rewrite.parse_id(),
                                       other_rewrite.type_of_change(),
                                       other_rewrite.realization,
                                       next_best.dependency_details_map)
            # Add both disambiguations at once
            option.disambiguations.extend([disambig, other_dis])
            options.append(option)
    # If combining the rewrites by matching types yields nothing
    if len(options) == 0:
        combined = combine_two_sided_rewrites(
            sentence)
        options.extend(combined)
    return options

#
# def combine_reversals_and_rewrites(sentence, parse, other_parse):
#     options = []
#     # Get reversals from one parse and rewrites from the other
#     valid_rewrites = [r for r in other_parse.rewrites if r.is_valid]
#     for rewrite in valid_rewrites:
#         option = DisambiguationOption(sentence)
#         reversal_realization = parse.reversal.realization
#         reversal = Disambiguation(parse.full_id,
#                                   DisambiguationOption.REVERSAL,
#                                   reversal_realization,
#                                   parse.dependency_details_map)
#         rewrite_option = Disambiguation(rewrite.parse_id(),
#                                         rewrite.type_of_change(),
#                                         rewrite.realization,
#                                         other_parse.dependency_details_map)
#         option.disambiguations.extend([reversal, rewrite_option])
#         options.append(option)
#     return options
