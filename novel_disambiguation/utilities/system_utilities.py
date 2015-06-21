__author__ = 'Ethan A. Hill'
import argparse
import logging
import os
import sys
import subprocess
import re
import math

from ..constants import ccg_values

__logger = logging.getLogger(__name__)


def total_available_ram():
    """Checks for the amount of available ram in the system.

    Returns:
        An integer value corresponding to the number of available processors
        in the system which this module is being executed in.
    """
    __logger.debug('Checking amount of available RAM.')
    # Check the operating system
    if 'linux' in sys.platform:
        __logger.debug('Using a %s OS.' % sys.platform)
        __logger.debug(
            'Executing command: free -g | grep Mem: | awk {print $2}')
        free_mem = subprocess.Popen(['free', '-g'], stdout=subprocess.PIPE)
        grep = subprocess.Popen(
            ['grep', 'Mem:'], stdin=free_mem.stdout, stdout=subprocess.PIPE)
        awk = subprocess.Popen(
            ['awk', '{print $2}'], stdin=grep.stdout, stdout=subprocess.PIPE)
        end_of_pipe = awk.stdout
        ram_list = [line.strip() for line in end_of_pipe]
        ram = ram_list[0]
    # ram is actually a string
    __logger.debug('{!s}G of RAM is available for system use.'.format(ram))
    return int(ram)


def maximum_ram_usage():
    path_expanded = os.path.expandvars(ccg_values.OPENCCG_BIN_ENV_FILE_PATH)
    __logger.debug(
        'Checking maximum RAM usage allowed by ccg file %s', path_expanded)
    with open(path_expanded) as bin_file:
        for line in bin_file:
            line_match = re.match(
                ccg_values.JAVA_MEMORY_VARIABLE_REGEX_STRING, line)
            if line_match:
                __logger.debug(
                    'Max RAM usage for ccg-build is %s', line_match.group(1))
                return int(line_match.group(1))
    __logger.warning('Could not find RAM usage limit in file %s', path_expanded)
    return 1


def max_threads_available():
    max_ram_usage = maximum_ram_usage()
    available_ram = total_available_ram()
    return int(math.ceil(available_ram / float(max_ram_usage)))


def total_effective_processes(num_jobs_to_process):
    __logger.debug('Calculating the number of effective threads '
                   'that can be created for processing files.')
    num_threads_available = max_threads_available()
    if num_threads_available > num_jobs_to_process:
        __logger.debug('Can create a thread for each job: '
                       '%d threads', num_jobs_to_process)
        return num_jobs_to_process
    else:
        __logger.debug('Can only create %d threads', num_threads_available)
        return num_threads_available


def initialize_arg_parser():
    __logger.debug('Initializing a command line argument parser.')

    parser = argparse.ArgumentParser(description='Generates disambiguating '
                                                 'paraphrases for ambiguities '
                                                 'appearing in novel text.')

    parser.add_argument('working_directory', metavar='wd', type=str,
                        help='specify the directory in which to find the text '
                             'files for processing. NOTE: The path to this '
                             'directory must be relative to '
                             '$OPENCCG_HOME/ccgbank By default, all files '
                             'found in this working directory will be used. To '
                             'target more specific files, use one of the '
                             'optional arguments.')

    parser.add_argument('-pp', '--post-process', action='store_true',
                        help='use when parsing/realization is not necessary')

    # It is probably easiest and best to make listing files an exclusive op
    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument('-l', '--include-list', nargs='+',
                        help='specify the file(s) to use. NOTE: these files '
                             'and these files ONLY will be processed. The file '
                             'names should be just the name without the path '
                             'prefixes, as these files should be found in the '
                             'specified working directory.')
    list_group.add_argument('-rl', '--reject-list', nargs='+',
                        help='specify the file(s) to reject. NOTE: files not '
                             'found in $OPENCCG_HOME/ccgbank/data/novel that '
                             'are NOT in this list WILL be used')
    list_group.add_argument('-f', '--include-list-file', nargs=1,
                        help='provide a file containing a list of files to '
                             'use, one file name (without the path prefix) per '
                             'line')
    list_group.add_argument('-rf', '--reject-list-file', nargs=1,
                        help='provide a file containing a list of files to '
                             'reject, one file name, (without the path prefix) '
                             'per line')
    parser.add_argument('-xd', '--xml-dump', nargs=1,
                        help='create an xml dump of paraphrases into this file '
                             'with details about each option')
    parser.add_argument('-od', '--option-dump', nargs=1,
                        help='create an xml dump of paraphrases into this file '
                             'with details about each option')

    # Any parsers that are to be used should exclusive options from each other
    parser_group = parser.add_mutually_exclusive_group()
    parser_group.add_argument('-b', '--berkeley-parser', action='store_true',
                              help='use the Berkeley parser instead of the '
                                   'ccg default')
    __logger.debug(
        'Initialized a command line argument parser with arguments %s', parser)
    return parser


def file_names_sorted_by_file_size(directory, file_list=None, reject=False):
    files = []
    if reject and file_list:
        __logger.debug('Gathering file names in directory %s, rejecting files '
                       'with the following names %s', directory, file_list)
        # Reject all files in the list
        for file_name in os.listdir(directory):
            if file_name not in file_list:
                files.append(os.path.join(directory, file_name))
    elif file_list:
        __logger.debug('Gathering the following files: %s ', file_list)
        # Gather all files listed
        for file_name in file_list:
            __logger.debug('Gathering file names from directory %s', directory)
            files.append(os.path.join(directory, file_name))
    else:
        # Gather all files in directory
        files = [os.path.join(directory, f) for f in os.listdir(directory)]
    # Filter out directories
    files = [f for f in files if not os.path.isdir(f)]
    __logger.debug('Sorting the following file names by file size: %s', files)
    file_size_dict = {}
    for file_name in files:
        absolute_path = os.path.abspath(file_name)
        file_size_dict[file_name] = os.path.getsize(absolute_path)
    __logger.debug('Sorted %d files by file size.', len(files))
    return sorted(file_size_dict, key=lambda x: file_size_dict[x])
