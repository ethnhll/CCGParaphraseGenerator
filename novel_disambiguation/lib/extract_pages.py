import mwclient
import wikipedia
import nltk.data
import re
import fileinput
import os
import shutil
import requests
import sys


def tokenize_into_sentences(text):
	sentences = tokenizer.tokenize(text)
	return sentences


def list_pages(category):
	global site, pages, subcategories
	print category
	for listing in site.Categories[category]:
		page_title = listing.page_title	
		# Allowing bird as a category brings in all text about birds, which is far more than dinosaurs... remove if you do want to see bird articles
		if page_title not in pages and page_title not in subcategories and 'bird' not in page_title.lower():
			if listing.namespace != 14:
				pages.add(page_title)
			else:
				subcategories.add(page_title)
				list_pages(page_title)

CATEGORY_NAMESPACE = 14
MAX_WORDS = 20
MIN_WORDS = 5

"""
'Big Ten Conference football' yields 6801 pages
'Dinosaurs by continental landmass' yields 1123 pages, ignore a page called Erketu,
it seems to only be URLs

'Dinosaurs' yields results for Birds....

"""

#CATEGORY = 'Dinosaurs by continental landmass'
CATEGORY = 'Prehistoric reptiles'

site = mwclient.Site('en.wikipedia.org')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

pages = set()
subcategories = set()
sentence_dict = {}
list_pages(CATEGORY)

pages_already_downloaded = set(os.listdir(os.path.join(os.getcwd(), CATEGORY)))
pages_dict = {re.sub(r'\W+', '', page): page for page in pages}
subbed_pages = set(pages_dict.keys())
pages_left = subbed_pages.difference(pages_already_downloaded)
pages_to_download = [pages_dict[subbed_page] for subbed_page in pages_left if subbed_page in pages_dict]
print "%s pages left to download" % len(pages_to_download)
count = 0
for page in pages_to_download:
	page_subbed = re.sub(r'\W+', '', page)
	try:
		page_path = os.path.join(os.getcwd(), '{!s}/{!s}'.format(CATEGORY, page_subbed))
		site_page = wikipedia.page(page)
		page_contents = tokenize_into_sentences(site_page.content.strip())
		filtered_sentences = []
		for sentence in page_contents:
			# Strip away whitespace (except the space itself) and the markup leftover
			filtered_sentence = re.sub(r'==.+==|[\t\n\r\f]+', ' ', sentence)
			filtered_sentence = filtered_sentence.strip()
			words = nltk.word_tokenize(filtered_sentence)
			# We are ignoring too short of sentences and too long of sentences
			if MIN_WORDS < len(words) <= MAX_WORDS:
				if not re.match(r'[^\x00-\x7F]+', filtered_sentence):
					tagged = nltk.pos_tag(words)
					# Only consider "complete sentences"
					if any('VB' == tag_tuple[1] for tag_tuple in tagged):
						filtered_sentence = filtered_sentence.encode('utf8')
						filtered_sentences.append(filtered_sentence)
		if filtered_sentences:
			with open(page_path, 'w') as sentence_file:
				for sentence in filtered_sentences:
					sentence_file.write(sentence + '\n')
		else:
			count += 1
	except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.HTTPTimeoutError, wikipedia.exceptions.RedirectError,
	        wikipedia.exceptions.WikipediaException, requests.exceptions.ConnectionError, UnicodeError):
		print "Error encountered, skipping page."
	except KeyboardInterrupt:
		page_path = os.path.join(os.getcwd(), '{!s}/{!s}'.format(CATEGORY, page_subbed))
		if os.path.exists(page_path):
			print "KeyboardInterrupt, deleting most recently looked at file."
			os.remove(page_path)
		sys.exit()
print count

