__author__ = 'hill1303'
import sys
from xml.etree import cElementTree as ElementTree

# Command arguments
xml_dump = sys.argv[1]
target_words_file = sys.argv[2]
form_output = sys.argv[3]

xml_root = ElementTree.parse(xml_dump).getroot()


sentences = xml_root.findall('.//sentence')

ambiguous_sentences = xml_root.findall(
    './/sentence[@ambiguous="True"]')

sentences_with_disambiguation = []
for sentence in ambiguous_sentences:
    if (sentence.find('parse/reversal[@valid="True"]') is not None or
            sentence.find('parse/rewrite[@valid="True"]') is not None):
        sentences_with_disambiguation.append(sentence)


target_words = set()
with open(target_words_file) as twf:
    for line in twf:
        target_words.add(line.strip())

sentences_with_disambiguations_with_target_words = []
for sentence in sentences_with_disambiguation:
    words = sentence.attrib.get('reference').strip().split()
    for word in words:
        if word in target_words:
            sentences_with_disambiguations_with_target_words.append(sentence)
            break

one_sided_options = []
for sentence in sentences_with_disambiguation:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        if ((parse_a.find('reversal[@valid="True"]') is not None or
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is None and
             parse_b.find('rewrite[@valid="True"]') is None)):
            one_sided_options.append(sentence)
        elif ((parse_b.find('reversal[@valid="True"]') is not None or
            parse_b.find('rewrite[@valid="True"]') is not None) and
            (parse_a.find('reversal[@valid="True"]') is None and
             parse_a.find('rewrite[@valid="True"]') is None)):
            one_sided_options.append(sentence)

one_sided_reversal_only = []
one_sided_rewrites_only = []
one_sided_both = []
for sentence in one_sided_options:
    if (sentence.find('parse/reversal[@valid="True"]') is not None and
            sentence.find('parse/rewrite[@valid="True"]') is not None):
        one_sided_both.append(sentence)
    elif (sentence.find('parse/reversal[@valid="True"]') is not None and
            sentence.find('parse/rewrite[@valid="True"]') is None):
        one_sided_reversal_only.append(sentence)
    elif (sentence.find('parse/reversal[@valid="True"]') is None and
            sentence.find('parse/rewrite[@valid="True"]') is not None):
        one_sided_rewrites_only.append(sentence)


two_sided_options = []
for sentence in sentences_with_disambiguation:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        if ((parse_a.find('reversal[@valid="True"]') is not None or
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is not None or
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_options.append(sentence)

two_sided_both_reversal_and_rewrite = []
for sentence in two_sided_options:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        if ((parse_a.find('reversal[@valid="True"]') is not None and
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is not None and
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_both_reversal_and_rewrite.append(sentence)

# These are not going to be used in the experiment
two_sided_only_mixed = []
for sentence in two_sided_options:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        if ((parse_a.find('reversal[@valid="True"]') is not None and
            parse_a.find('rewrite[@valid="True"]') is None) and
            (parse_b.find('reversal[@valid="True"]') is None and
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_only_mixed.append(sentence)
        elif ((parse_a.find('reversal[@valid="True"]') is None and
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is not None and
             parse_b.find('rewrite[@valid="True"]') is None)):
            two_sided_only_mixed.append(sentence)

two_sided_mixed = []
for sentence in two_sided_options:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        # One side is missing rewrites
        if ((parse_a.find('reversal[@valid="True"]') is not None and
            parse_a.find('rewrite[@valid="True"]') is None) and
            (parse_b.find('reversal[@valid="True"]') is not None and
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_mixed.append(sentence)
        elif ((parse_a.find('reversal[@valid="True"]') is not None and
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is not None and
             parse_b.find('rewrite[@valid="True"]') is None)):
            two_sided_mixed.append(sentence)
            # One side is missing reversals
        if ((parse_a.find('reversal[@valid="True"]') is None and
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is not None and
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_mixed.append(sentence)
        elif ((parse_a.find('reversal[@valid="True"]') is not None and
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is None and
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_mixed.append(sentence)


two_sided_only_reversals = []
for sentence in two_sided_options:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        if ((parse_a.find('reversal[@valid="True"]') is not None and
            parse_a.find('rewrite[@valid="True"]') is None) and
            (parse_b.find('reversal[@valid="True"]') is not None and
             parse_b.find('rewrite[@valid="True"]') is None)):
            two_sided_only_reversals.append(sentence)

two_sided_only_rewrites = []
for sentence in two_sided_options:
    parses = sentence.findall('parse')
    if len(parses) == 2:
        parse_a, parse_b = parses
        if ((parse_a.find('reversal[@valid="True"]') is None and
            parse_a.find('rewrite[@valid="True"]') is not None) and
            (parse_b.find('reversal[@valid="True"]') is None and
             parse_b.find('rewrite[@valid="True"]') is not None)):
            two_sided_only_rewrites.append(sentence)

sentences_with_valid_reversal = xml_root.findall(
    './/sentence/parse/reversal[@valid="True"]/../..')
sentences_with_valid_rewrites = xml_root.findall(
    './/sentence/parse/rewrite[@valid="True"]/../..')

sentences_with_both = []
for sentence in sentences:
    if (sentence.find('parse/reversal[@valid="True"]') is not None and
            sentence.find('parse/rewrite[@valid="True"]') is not None):
        sentences_with_both.append(sentence)


sentences_only_valid_rewrites = []
for sentence in sentences_with_valid_rewrites:
    if sentence.find('parse/reversal[@valid="True"]') is None:
        sentences_only_valid_rewrites.append(sentence)

sentences_only_valid_reversals = []
for sentence in sentences_with_valid_reversal:
    if sentence.find('parse/rewrite[@valid="True"]') is None:
        sentences_only_valid_reversals.append(sentence)

print 'sentences:', len(sentences)
print 'ambiguous sentences:', len(ambiguous_sentences)
print 'sentences with a disambiguation:', len(sentences_with_disambiguation)
print 'sentences with disambiguation with target word:', len(
    sentences_with_disambiguations_with_target_words)
print 'sentences with one sided option:', len(one_sided_options)
print '\tone sided with both:', len(one_sided_both)
print '\tone sided with reversals only:', len(one_sided_reversal_only)
print '\tone sided with rewrites only:', len(one_sided_rewrites_only)

print 'sentences with two sided option:', len(two_sided_options)
print '\ttwo sided with both on either side', len(two_sided_both_reversal_and_rewrite)
print '\ttwo sided with reversal on one side, rewrite the other', len(two_sided_only_mixed)
print '\ttwo sided with only reversals:', len(two_sided_only_reversals)
print '\ttwo sided with only rewrites:', len(two_sided_only_rewrites)
print '\ttwo sided mixed:', len(two_sided_mixed)
print 'sentences with both rewrites and reversals', len(sentences_with_both)
print 'sentences with valid reversal:', len(sentences_with_valid_reversal)
print 'sentences with only valid reversals:', len(sentences_only_valid_reversals)
print 'sentences with valid rewrites:', len(sentences_with_valid_rewrites)
print 'sentences with only valid rewrites:', len(sentences_only_valid_rewrites)



TOTAL_OPTIONS = 515
SINGLE_OPTIONS = 145
DOUBLE_OPTIONS = 370
REVERSALS = 250
REWRITES = DOUBLE_OPTIONS - REVERSALS
TOTAL_TARGET = 258