__author__ = 'Ethan A. Hill'
import logging
import os
import subprocess
from ..constants import ccg_values


__logger = logging.getLogger(__name__)


def ccg_build_parse(path_to_text, use_berkeley_target=False):
    # We need to check a few things before running this process
    # TODO: Change these asserts to Exceptions...
    #   1) Are we currently in the correct directory?
    #   2) Does the file we passed in exist?
    #       a) TODO: The file path must be relative to the ccgbank path for now
    bank_path_expanded = os.path.expandvars(ccg_values.CCGBANK_PATH)
    assert os.getcwd() == bank_path_expanded, (
        'working directory %s is not %s' % (os.getcwd(), bank_path_expanded))
    full_path_to_text = os.path.join(bank_path_expanded, path_to_text)
    assert os.path.exists(full_path_to_text), (
        '%s does not exist' % full_path_to_text)

    if use_berkeley_target:
        target = 'test-bklParser-novel'
    else:
        target = 'test-parser-novel-nbest'

    __logger.debug('Attempting to parse %s using target %s.',
                   full_path_to_text, target)
    process_output = subprocess.check_output(
        ['ccg-build', '-Dnovel.file=%s' % path_to_text, '-f', 'build-ps.xml',
         target], stderr=subprocess.STDOUT, shell=False)

    __logger.debug('Finished parsing %s with captured output %s',
                   path_to_text, process_output)

    return process_output


def ccg_build_realize(path_to_text, use_berkeley_target=False):

    # We need to check a few things before running this process
    # TODO: Change these asserts to Exceptions...
    #   1) Are we currently in the correct directory?
    #   2) Does the file we passed in exist?
    #       a) TODO: The file path must be relative to the ccgbank path for now
    bank_path_expanded = os.path.expandvars(ccg_values.CCGBANK_PATH)
    assert os.getcwd() == bank_path_expanded, (
        'working directory %s is not %s' % (os.getcwd(), bank_path_expanded))
    full_path_to_text = os.path.join(bank_path_expanded, path_to_text)
    assert os.path.exists(full_path_to_text), (
        '%s does not exist' % full_path_to_text)

    target = 'test-bklParser-novel' if use_berkeley_target else 'test-novel'
    __logger.debug('Attempting to realize %s using target %s.',
                   full_path_to_text, target)
    process_output = subprocess.check_output(
        ['ccg-build', '-Dnovel.file=%s' % path_to_text, '-f', 'build-rz.xml',
         target], stderr=subprocess.STDOUT, shell=False)
    __logger.debug('Finished realizing %s with captured output %s',
                   path_to_text, process_output)
    return process_output