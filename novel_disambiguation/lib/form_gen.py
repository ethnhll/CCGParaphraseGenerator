from collections import defaultdict
import sys
import math
import os
import subprocess
import shutil
import csv
import re
import difflib
from xml.etree import cElementTree as ElementTree


def disambiguation_key(disambig):
    disambig_id = disambig.attrib.get('parse_id')
    sent_id, parse_number = disambig_id.split('-')
    sentence_number = int(sent_id[1:])
    parse_number = int(parse_number)
    return sentence_number, parse_number


def underline_changes_in_disambiguation(reference, realization):
    reference_sequence = reference.split()
    disambiguation_sequence = realization.split()

    differences = list(difflib.Differ().compare(reference_sequence,
                                                disambiguation_sequence))
    changed_sequence = [word[2:] for word in differences if
                        word.startswith('+ ')]

    seq = difflib.SequenceMatcher(None, disambiguation_sequence,
                                  changed_sequence)
    matches = seq.get_matching_blocks()
    capitalized_sequence = realization.capitalize().split()
    # Ignoring last dummy match
    for match in matches[:len(matches) - 1]:
        start = match.a
        end = start + match.size - 1
        capitalized_sequence[start] = '<u>{}'.format(
            capitalized_sequence[start])
        capitalized_sequence[end] = '{}</u>'.format(
            capitalized_sequence[end])
    realization = ' '.join(capitalized_sequence)
    return realization


def generate_dependency_graphs(output_directory):
    graphs_directory = os.path.join(output_directory, 'graphs')
    if not os.path.exists(graphs_directory):
        os.mkdir(graphs_directory)
    if not os.listdir(graphs_directory):
        test_bed = os.path.join(output_directory, 'tb.xml')
        subprocess.check_output(
            ['ccg-draw-graph', '-i', '%s' % test_bed,
            '-v', '%s/g' % graphs_directory], stderr=subprocess.STDOUT,
            shell=False)

# Command arguments
xml_dump = sys.argv[1]
target_words_file = sys.argv[2]
DATA_NOVEL_DIRECTORY = sys.argv[3]
output_sub_options_xml = sys.argv[4]

tree = ElementTree.parse(xml_dump)


options = [option for option in tree.getroot().findall('.//option')]

single_sided = [element for element in tree.getroot() if
                element.attrib.get('double_sided') == 'False']
double_sided = [element for element in tree.getroot() if
                element.attrib.get('double_sided') == 'True']

target_words = set()
with open(target_words_file) as twf:
    for line in twf:
        target_words.add(line.strip())
options_with_targets = []
for option in options:
    words = option.attrib.get('reference').strip().split()
    for word in words:
        if word in target_words:
            options_with_targets.append(option)
            break


print len(options)

single_reversal = []
for element in single_sided:
    if len(element.findall('disambiguation[@type="reversal"][@valid="True"]')) == 1:
        single_reversal.append(element)

single_rewrite = []
for element in single_sided:
    disambiguations = element.findall('disambiguation[@valid="True"]')
    if len(disambiguations) == 1:
        option = disambiguations[0]
        if option.attrib.get('type') != 'reversal':
            single_rewrite.append(element)

double_reversal = []
for element in double_sided:
    if len(element.findall('disambiguation[@type="reversal"][@valid="True"]')) == 2:
        double_reversal.append(element)

double_rewrite = []
for element in double_sided:
    disambiguations = element.findall('disambiguation[@valid="True"]')
    if len(disambiguations) == 2:
        rewrite_a, rewrite_b = disambiguations
        # Ignore the reversals, those are already taken care of
        if rewrite_a.attrib.get('type') == rewrite_b.attrib.get('type') and rewrite_a.attrib.get('type') != 'reversal':
            double_rewrite.append(element)
print len(single_sided), ',', len(double_sided)
print len(single_reversal), len(single_rewrite), ',', len(double_reversal), len(
    double_rewrite)
print 'with targets:', len(options_with_targets)


TOTAL_OPTIONS = 515
SINGLE_OPTIONS = 145
DOUBLE_OPTIONS = 370
DOUBLE_REVERSALS = 250
DOUBLE_REWRITES = DOUBLE_OPTIONS - DOUBLE_REVERSALS
TOTAL_TARGET = 258
TARGET_DOUBLE = int(math.ceil(DOUBLE_OPTIONS / float(2)))
TARGET_SINGLE = TOTAL_TARGET - TARGET_DOUBLE
SINGLE_REVERSALS = int(math.ceil(SINGLE_OPTIONS * (DOUBLE_REVERSALS/float(DOUBLE_OPTIONS))))
SINGLE_REWRITES = SINGLE_OPTIONS - SINGLE_REVERSALS

seen_sentences = defaultdict(int)

single_count = 0
single_target_count = 0
single_reversal_count = 0
single_rewrite_count = 0
single_options_for_print = []
single_reversal_target = [o for o in single_reversal if o in options_with_targets]
for option in single_reversal_target:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    if seen_sentences[text_file, sentence_id] < 3:
        if single_reversal_count < SINGLE_REVERSALS:
            single_options_for_print.append(option)
            single_reversal_count += 1
            single_target_count += 1
            single_count += 1
            seen_sentences[text_file, sentence_id] += 1

single_rewrite_target = [o for o in single_rewrite if o in options_with_targets]
for option in single_rewrite_target:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    if seen_sentences[text_file, sentence_id] < 3:
        if single_rewrite_count < SINGLE_REWRITES:
            single_options_for_print.append(option)
            single_rewrite_count += 1
            single_target_count += 1
            single_count += 1
            seen_sentences[text_file, sentence_id] += 1
print len(single_options_for_print)

# There wont be enough sentences in some cases with targets, so we add them first

double_count = 0
double_target_count = 0
double_reversal_count = 0
double_rewrite_count = 0
double_options_for_print = []

double_reversal_target = [o for o in double_reversal if o in options_with_targets]
for option in double_reversal_target:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    if seen_sentences[text_file, sentence_id] < 3:
        if double_reversal_count < DOUBLE_REVERSALS:
            double_options_for_print.append(option)
            double_reversal_count += 1
            double_target_count += 1
            double_count += 1
            seen_sentences[text_file, sentence_id] += 1


double_reversal_non_target = [o for o in double_reversal if o not in options_with_targets]
for option in double_reversal_non_target:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    if seen_sentences[text_file, sentence_id] < 3:
        if double_reversal_count < DOUBLE_REVERSALS:
            double_options_for_print.append(option)
            double_reversal_count += 1
            double_count += 1
            seen_sentences[text_file, sentence_id] += 1

double_rewrite_targets_matching = [o for o in double_rewrite if o in options_with_targets]
already_added = []
for option in double_rewrite_targets_matching:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    # Add rewrites that might have matching counter parts in the reversals
    if seen_sentences[text_file, sentence_id] < 3 and seen_sentences[text_file, sentence_id] >= 1:
        if double_rewrite_count < DOUBLE_REWRITES:
            double_options_for_print.append(option)
            already_added.append(option)
            double_rewrite_count += 1
            double_target_count += 1
            double_count += 1
            seen_sentences[text_file, sentence_id] += 1

# Now add double targets as usual
double_rewrite_targets_matching = [o for o in double_rewrite if o in options_with_targets and o not in already_added]
for option in double_rewrite_targets_matching:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    # Add rewrites that might have matching counter parts in the reversals
    if seen_sentences[text_file, sentence_id] < 3:
        if double_rewrite_count < DOUBLE_REWRITES:
            double_options_for_print.append(option)
            double_rewrite_count += 1
            double_target_count += 1
            double_count += 1
            seen_sentences[text_file, sentence_id] += 1

to_print = single_options_for_print + double_options_for_print

output_xml_root = ElementTree.Element('novel_disambiguation')
for option in to_print:
    output_xml_root.append(option)
output_xml_tree = ElementTree.ElementTree(output_xml_root)
output_xml_tree.write(output_sub_options_xml, encoding='utf-8')


print len(to_print)

to_print_paths = []
seen_files = set()
for form in to_print:
    text_file = form.attrib.get('text_file')
    sentence_id = form.attrib.get('sentence_id')
    file_match = re.match('^.*/(.*)$', text_file)
    text_file = file_match.group(1)
    if text_file not in seen_files:
        print 'generating graphs for %s' % text_file
        # Before we mess with the name, generate the dependency graphs
        generate_dependency_graphs(
            '{}/{}.dir'.format(DATA_NOVEL_DIRECTORY, text_file))
        seen_files.add(text_file)

    text_file = '_'.join([text_file, sentence_id])
    subs = form.findall('disambiguation[@valid="True"]')
    for sub in subs:
        text_file += '_%s' % sub.attrib.get('type')


    to_print_paths.append(text_file)

with open('annotations.tsv', 'w') as annotate:
    writer = csv.writer(annotate, delimiter='\t', quotechar="'",
                        quoting=csv.QUOTE_ALL)
    writer.writerow(
        ['text_file', 'sentence_id', 'num_options', 'top/next_best/neither',
         'comments'])

    for i, form in enumerate(to_print):
        text_file = form.attrib.get('text_file')
        file_match = re.match('^.*/(.*)$', text_file)
        # save this for later
        text_file_name = file_match.group(1)

        sentence_id = form.attrib.get('sentence_id')
        reference = form.attrib.get('reference')
        double_sided = form.attrib.get('double_sided')

        text_file = '_'.join([text_file_name, sentence_id])
        subs = form.findall('disambiguation[@valid="True"]')
        for sub in subs:
            text_file += '_%s' % sub.attrib.get('type')

        num_options = 2 if double_sided == 'True' else 1

        writer.writerow([text_file, sentence_id, num_options, ' ', ' '])

        with open(text_file, 'w') as html_out:

            html_out.write('<!DOCTYPE html>\n')
            html_out.write('<html>\n')
            html_out.write('\t<head>\n')
            html_out.write('\t\t<meta charset="utf-8" />\n')
            html_out.write(
                '\t\t<title>Sentence Disambiguation: {!s} </title>\n'.format(
                    text_file))
            html_out.write('\t</head>\n')
            html_out.write('\t<body>\n')

            html_out.write(
                '\t\t<h1>ID: {}</h1>\n'.format(text_file))
            html_out.write('\t\t<hr></hr>\n')

            if i == 0 and len(to_print) > 1:
                html_out.write(
                    '\t\t<a href="{!s}">NEXT</a>'.format(to_print_paths[i + 1]))
            elif i > 0 and i < len(to_print) - 1:
                html_out.write('\t\t<a href="{!s}"><--PREVIOUS </a> '.format(
                    to_print_paths[i - 1]))
                html_out.write(
                    '<a href="{!s}">NEXT--></a>'.format(to_print_paths[i + 1]))
            elif i == len(to_print) - 1:
                html_out.write('\t\t<a href="{!s}"><--PREVIOUS </a>'.format(
                    to_print_paths[i - 1]))



            html_out.write('\t\t<h3><u>Reference Sentence</u></h3>\n')
            html_out.write('\t\t<p>%s</p>\n' % reference.capitalize().encode('utf8'))

            option_sides = 'Double-Sided' if double_sided == 'True' else 'Single-Sided'

            html_out.write(
                '\t\t<h3><u>Disambiguations</u>: %s</h3>\n' % option_sides)

            disambiguations = [disambig for disambig in form if disambig.tag == 'disambiguation']
            for disambiguation in sorted(disambiguations, key=disambiguation_key):
                parse_id = disambiguation.attrib.get('parse_id')
                type_ = disambiguation.attrib.get('type')
                valid = disambiguation.attrib.get('valid')
                realization = disambiguation.attrib.get('realization').capitalize() if disambiguation.attrib.get('realization') else 'None'
                realization = underline_changes_in_disambiguation(
                                reference, realization.encode('utf8'))

                ambig_dependencies = []
                unambig_dependencies = []

                print 'Copying over files for %s' % text_file
                shutil.copyfile('{}/{}.dir/graphs/g.{}.0.pdf'.format(
                    DATA_NOVEL_DIRECTORY, text_file_name, parse_id),
                                '{}/{}.{}.pdf'.format(os.getcwd(), text_file,
                                                      parse_id))

                for details in disambiguation:
                    if details.tag == 'dependencies':
                        for dependency in details:
                            head = dependency.attrib.get('head')
                            dependent = dependency.attrib.get('dependent')
                            dependency_string = 'head={!s} , dependent={!s}'.format(head, dependent)
                            if dependency.attrib.get('ambiguous') == 'True':
                                ambig_dependencies.append(
                                    dependency_string)
                            unambig_dependencies.append(dependency_string)

                html_out.write(
                    '\t\t<p><strong>Realization:</strong> %s</p>\n' % realization)
                html_out.write(
                    '\t\t<p>Type: {}, Validated: {}, Parse ID: {}</p>\n'.format(type_, valid, parse_id))
                html_out.write(
                    '\t\t<a href="{}.{}.pdf"><strong>Dependencies (click for graph)</strong></a>\n'.format(
                        text_file, parse_id))
                for depend in ambig_dependencies:
                    html_out.write('\t\t<p><strong>%s</strong></p>\n' % depend)
                for depend in unambig_dependencies:
                    html_out.write('\t\t<p>%s</p>\n' % depend)
                html_out.write('\t\t</br>\n')

            if i == 0 and len(to_print) > 1:
                html_out.write(
                    '\t\t<a href="{!s}">NEXT</a>'.format(to_print_paths[i + 1]))
            elif i > 0 and i < len(to_print) - 1:
                html_out.write('\t\t<a href="{!s}"><--PREVIOUS </a> '.format(
                    to_print_paths[i - 1]))
                html_out.write(
                    '<a href="{!s}">NEXT--></a>'.format(to_print_paths[i + 1]))
            elif i == len(to_print) - 1:
                html_out.write('\t\t<a href="{!s}"><--PREVIOUS </a>'.format(
                    to_print_paths[i - 1]))

            html_out.write('\n\t</body>\n')