from collections import defaultdict
import math

__author__ = 'hill1303'
import sys
from random import shuffle
from xml.etree import cElementTree as ElementTree

# Command arguments
xml_dump = sys.argv[1]
target_words_file = sys.argv[2]

tree = ElementTree.parse(xml_dump)


options = [option for option in tree.getroot().findall('.//option')]
shuffle(options)
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


same_as_reference = []
for option in options:
    reference = option.attrib.get('reference')
    same_option = option.find('disambiguation[@realization="%s"]' % reference)
    if same_option:
        same_as_reference.append(option)


print 'Number of options:', len(options)

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
matching_reversals = []
for element in double_sided:
    disambiguations = element.findall('disambiguation[@type="reversal"][@valid="True"]')
    if len(disambiguations) == 2:
        double_reversal.append(element)
        disambig_a, disambig_b = disambiguations
        if disambig_a.attrib.get('realization') == disambig_b.attrib.get('realization'):
            matching_reversals.append(element)


double_rewrite = []
matching_rewrites = []
for element in double_sided:
    disambiguations = element.findall('disambiguation[@valid="True"]')
    if len(disambiguations) == 2:
        rewrite_a, rewrite_b = disambiguations
        # Ignore the reversals, those are already taken care of
        if rewrite_a.attrib.get('type') == rewrite_b.attrib.get('type') and rewrite_a.attrib.get('type') != 'reversal':
            double_rewrite.append(element)
            if rewrite_a.attrib.get('realization') == rewrite_b.attrib.get('realization'):
                matching_rewrites.append(element)
to_print = []
print 'Single sided:', len(single_sided), ',', 'Double sided:', len(double_sided)
print 'Single reversals:', len(single_reversal), 'Single rewrites:', len(single_rewrite), ',', 'Double reversals:', len(double_reversal), 'Double rewrites:', len(
    double_rewrite)
print 'with targets:', len(options_with_targets)
print 'doubles with matching realizations:', len(matching_rewrites)
print 'doubles with matching reversals:', len(matching_reversals)
print 'options with realization same as reference:', len(same_as_reference)


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
for option in double_rewrite_targets_matching:
    sentence_id = option.attrib.get('sentence_id')
    text_file = option.attrib.get('text_file')
    # Add rewrites that might have matching counter parts in the reversals
    if seen_sentences[text_file, sentence_id] < 3 and seen_sentences[text_file, sentence_id] >= 1:
        if double_rewrite_count < DOUBLE_REWRITES:
            double_options_for_print.append(option)
            double_rewrite_count += 1
            double_target_count += 1
            double_count += 1
            seen_sentences[text_file, sentence_id] += 1

# Now add double targets as usual
double_rewrite_targets_matching = [o for o in double_rewrite if o in options_with_targets]
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


print len(double_options_for_print + single_options_for_print)