__author__ = 'Ethan A. Hill'
import logging
import build_utilities
import sentence_utilities
import rewrite_utilities
import reversal_utilities
from ..utilities import option_utilities


__logger = logging.getLogger(__name__)


def disambiguate(path_to_text, post_process=False):
    parse_output_directory = '%s.dir' % path_to_text
    __logger.debug('Processing text file %s into directory %s',
                   path_to_text, parse_output_directory)
    # We only want to parse if we are not to post process things
    if not post_process:
        __logger.debug('Parsing text file %s ', path_to_text)
        build_utilities.ccg_build_parse(path_to_text)
    sentences = sentence_utilities.sentence_factory(parse_output_directory)
    # Apply rewrites if we can...
    rewrite_utilities.apply_rewrites(sentences, parse_output_directory)
    if not post_process:
        __logger.debug('Realizing parses for %s ', path_to_text)
        build_utilities.ccg_build_realize(path_to_text)
    rewrite_utilities.validate_rewrites(sentences, parse_output_directory)
    path_to_reparse_text = reversal_utilities.prepare_reversals(
        sentences, parse_output_directory)
    # Now reparse the newly created reversals
    if not post_process:
        __logger.debug('Parsing text file %s ', path_to_reparse_text)
        build_utilities.ccg_build_parse(path_to_reparse_text)

    reversal_utilities.validate_reversals(sentences, parse_output_directory)
    __logger.debug('Finished processing text file %s into directory %s',
                   path_to_text, parse_output_directory)
    return sentences


def disambiguation_worker(job_queue, output_queue, post_process=False):
    while True:
        item = job_queue.get()
        # Process tasks as they come into the queue
        __logger.info('Attempting to process %s with %d files left to '
                      'process...', item, job_queue.qsize())
        try:
            # Do work, item is positional, we don't know about the others
            captured_output = disambiguate(item, post_process)
            output_queue.put(captured_output)
        except Exception, e:
            __logger.exception('Exception %s encountered, skipping %s', e, item)
            pass
        finally:
            __logger.info('Finished processing %s', item)
            job_queue.task_done()
    return output_queue


def gather_disambiguation_options(sentences):
    # Obviously only ambiguous sentences can have utilities options
    ambiguous = [sentence for sentence in sentences if sentence.is_ambiguous()]
    options = []
    for sentence in ambiguous:
        # Add all options at once
        options.extend(option_utilities.options_factory(sentence))
    return options
