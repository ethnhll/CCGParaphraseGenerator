#!/usr/bin/python
__author__ = 'Ethan A. Hill'
import itertools
import threading
import logging
import logging.config
import os
from Queue import Queue
from xml.etree import cElementTree as ElementTree

from constants import ccg_values
from utilities import system_utilities
from utilities import disambig_utilities


def gather_file_names_from_arguments(arguments):
    working_directory = arguments.working_directory
    if arguments.include_list:
        # Explicit listing of files to process
        files = system_utilities.file_names_sorted_by_file_size(
            working_directory, file_list=arguments.include_list, reject=False)

    elif arguments.reject_list:
        # Explicit listing of files to reject, process all others
        files = system_utilities.file_names_sorted_by_file_size(
            working_directory, file_list=arguments.reject_list, reject=True)

    elif arguments.include_list_file:
        # We have a file with a list of file names to process
        include_file_path = os.path.abspath(arguments.include_list_file[0])
        with open(include_file_path) as f:
            file_list = [l.rstrip() for l in f.readlines()]
        files = system_utilities.file_names_sorted_by_file_size(
            working_directory, file_list=file_list, reject=False)

    elif arguments.reject_list_file:
        # We have a file with list of file names to reject, process all others
        include_file_path = os.path.abspath(arguments.reject_list_file[0])
        with open(include_file_path) as f:
            file_list = [l.rstrip() for l in f.readlines()]
        files = system_utilities.file_names_sorted_by_file_size(
            working_directory, file_list=file_list, reject=True)

    else:
        files = set(system_utilities.file_names_sorted_by_file_size(
            working_directory))
    return files


def setup_logger(package_path):
    # If for some reason the logs folder was removed, recreate it
    log_folder = os.path.join(package_path, 'logs')
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Setup 3 handlers
    log_file = os.path.join(log_folder, 'debug.log')
    log_file_handler = logging.FileHandler(log_file, mode='w')
    log_file_handler.setLevel(logging.DEBUG)
    detailed_formatter = logging.Formatter(
        '[THREAD:%(threadName)s MODULE:%(module)s '
        'FILE_LINE:%(filename)s:%(lineno)d] %(levelname)s: %(message)s')
    log_file_handler.setFormatter(detailed_formatter)

    # We want to see only errors in this log file
    error_log_file = os.path.join(log_folder, 'error.log')
    error_log_file_handler = logging.FileHandler(error_log_file, mode='w')
    error_log_file_handler.setLevel(logging.ERROR)
    simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
    error_log_file_handler.setFormatter(simple_formatter)

    # We just want to see pertinent information on the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)

    # Add all of the handlers to the logger
    handlers = [log_file_handler, error_log_file_handler, console_handler]
    for handler in handlers:
        logger.addHandler(handler)
    return logger


def further_processing(arguments, sentences):
    if arguments.xml_dump:
        xml_file_path = arguments.xml_dump[0]
        xml_root = ElementTree.Element('raw_data')
        for sentence in sentences:
            xml_root.append(sentence.xmlize())
        xml_tree = ElementTree.ElementTree(xml_root)
        xml_tree.write(xml_file_path, encoding='utf-8')
    if arguments.option_dump:
        xml_file_path = arguments.option_dump[0]
        xml_root = ElementTree.Element('novel_disambiguation')
        options = disambig_utilities.gather_disambiguation_options(sentences)
        for option in options:
            xml_root.append(option.xmlize())
        xml_tree = ElementTree.ElementTree(xml_root)
        xml_tree.write(xml_file_path, encoding='utf-8')

def main(arguments):
    original_working_directory = os.getcwd()
    # Change our working directory to CCGBANK_PATH
    os.chdir(os.path.expandvars(ccg_values.CCGBANK_PATH))

    text_files = gather_file_names_from_arguments(arguments)
    # Find out how many threads we can make for this task
    num_threads = system_utilities.total_effective_processes(len(text_files))

    job_queue, out_queue = Queue(), Queue()
    # range is end value exclusive
    for thread_number in xrange(1, num_threads + 1):
        thread = threading.Thread(
            target=disambig_utilities.disambiguation_worker,
            args=(job_queue, out_queue, ),
            kwargs={'post_process': arguments.post_process})
        thread.daemon = True
        thread.start()
    # Dump the text files in for processing
    for text_file in text_files:
        job_queue.put(text_file)
    job_queue.join()

    sentence_sets = list(out_queue.queue)
    # Reduce the sentence sets to a single list of sentences for processing
    sentences = list(itertools.chain.from_iterable(sentence_sets))

    further_processing(arguments, sentences)

    os.chdir(original_working_directory)


# This is used for logging...
__package_path = os.path.dirname(__file__)
# Initialize some things before getting started...
__logger = setup_logger(__package_path)
if __name__ == '__main__':
    argument_parser = system_utilities.initialize_arg_parser()
    main(argument_parser.parse_args())