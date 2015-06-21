import collections

__author__ = 'hill1303'
import sys
from xml.etree import cElementTree as ElementTree

xml_dump = sys.argv[1]
ptb_word_count_file = sys.argv[2]
output_target_words = sys.argv[3]

xml_root = ElementTree.parse(xml_dump).getroot()
sentences = xml_root.findall('.//sentence')


ptb_counter = collections.Counter()
with open(ptb_word_count_file) as ptb_file:
    for line in ptb_file:
        word, count = line.strip().split()
        ptb_counter.update({word: int(count)})

ptb_most_common = set()
for word, count in ptb_counter.most_common(5000):
    ptb_most_common.add(word)

data_word_counter = collections.Counter()
for sentence in sentences:
    words = sentence.attrib.get('reference').strip().split()
    data_word_counter.update(words)
difference = set(data_word_counter.keys()) - ptb_most_common

difference_data_counter = collections.Counter()
for key in difference:
     count = data_word_counter[key]
     difference_data_counter.update({key: count})

with open(output_target_words, 'w') as out_file:
    for word, count in difference_data_counter.most_common(100):
        out_file.write(word + '\n')