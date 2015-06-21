__author__ = 'Ethan A. Hill'

TEST_EMPTY_TEXT_FILE = 'test_empty'
TEST_ONE_SENTENCE_TEXT_FILE = 'test_one_sentence'
FULL_PATH_DATA_NOVEL = '$OPENCCG_HOME/ccgbank/data/novel'
SUB_PATH_DATA_NOVEL = 'data/novel'
REALIZATIONS = 'realize.nbest'
LOGICAL_FORM = 'tb.xml'


BUILD_SUCCESS_MESSAGE = 'BUILD SUCCESSFUL'
EXCEPTION_MESSAGE = 'Exception'


TEST_TEXT_FILE = 'two-sents'


DATA_SUB_TEST_SENTENCES = 'data/novel/two-sents'
DATA_SUB_TEST_DIRECTORY = 'data/novel/two-sents.dir'
DATA_SUB_TEST_LF = 'data/novel/two-sents.dir/tb.xml'
DATA_SUB_TEST_REALIZATIONS = 'data/novel/two-sents.dir/realize.nbest'

FULL_PATH_TEST_SENTENCES = '$OPENCCG_HOME/ccgbank/data/novel/two-sents'
FULL_PATH_TEST_DIR = '$OPENCCG_HOME/ccgbank/data/novel/two-sents.dir'
FULL_PATH_TEST_LF = '$OPENCCG_HOME/ccgbank/data/novel/two-sents.dir/tb.xml'
FULL_PATH_TEST_REALIZATIONS = '$OPENCCG_HOME/ccgbank/data/novel/two-sents.dir/tb.xml'
TEST_BUILD_SUCCESSFUL = 'BUILD SUCCESSFUL'

# This is the preprocessed sentence, not the exact one that appears in the file
TEST_REFERENCE = ('Google announced today that it would offer free texting on '
                  'its Google_Voice app for the iPhone .')

TEST_UNLABELED_DEPENDENCIES = {('offer', 'it'), ('texting', 'on'),
                               ('texting', 'free'), ('announced', 'Google'),
                               ('app', 'for'), ('for', 'iPhone'),
                               ('on', 'app'), ('iPhone', 'the'),
                               ('would', 'it'), ('announced', 'today'),
                               ('offer', 'texting'), ('would', 'offer'),
                               ('app', 'its'), ('app', 'Google_Voice'),
                               ('announced', 'would')}

TEST_DEPENDENCY_DETAILS = {(('announced', 1, 'VBD', 'announce.01'),
                            ('Google', 0, 'NNP', 'Google')), (
                               ('texting', 8, 'NN', 'texting'),
                               ('free', 7, 'RB', 'free')), (
                               ('app', 12, 'NN', 'app'),
                               ('for', 13, 'IN', 'for')), (
                               ('app', 12, 'NN', 'app'),
                               ('Google_Voice', 11, 'NNP',
                                'Google_Voice')), (
                               ('announced', 1, 'VBD', 'announce.01'),
                               ('would', 5, 'MD', 'would')), (
                               ('on', 9, 'IN', 'on'),
                               ('app', 12, 'NN', 'app')), (
                               ('would', 5, 'MD', 'would'),
                               ('offer', 6, 'VB', 'offer.01')), (
                               ('iPhone', 15, 'NN', 'iPhone'),
                               ('the', 14, 'DT', 'the')), (
                               ('offer', 6, 'VB', 'offer.01'),
                               ('texting', 8, 'NN', 'texting')), (
                               ('app', 12, 'NN', 'app'),
                               ('its', 10, 'PRP$', 'its')), (
                               ('for', 13, 'IN', 'for'),
                               ('iPhone', 15, 'NN', 'iPhone')), (
                               ('texting', 8, 'NN', 'texting'),
                               ('on', 9, 'IN', 'on')), (
                               ('would', 5, 'MD', 'would'),
                               ('it', 4, 'PRP', 'it')), (
                               ('offer', 6, 'VB', 'offer.01'),
                               ('it', 4, 'PRP', 'it')), (
                               ('announced', 1, 'VBD', 'announce.01'),
                               ('today', 2, 'NN', 'today'))}