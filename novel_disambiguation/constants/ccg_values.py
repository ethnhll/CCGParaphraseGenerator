__author__ = 'Ethan A. Hill'

# These paths are essential for most build commands/utilities
OPENCCG_HOME_PATH = '$OPENCCG_HOME'
CCGBANK_PATH = '$OPENCCG_HOME/ccgbank'
OPENCCG_BIN_ENV_FILE_PATH = '$OPENCCG_HOME/bin/ccg-env'

JAVA_MEMORY_VARIABLE_REGEX_STRING = '^JAVA_MEM="-Xmx([0-9]+).*"$'

# Constants for tests
DATA_NOVEL_SUB_PATH = 'data/novel'

# Verb conjugations
BE_VERB_FORMS = ['be', 'been', 'being', 'is', 'was', 'were', 'am', 'are']
DO_VERB_FORMS = ['do', 'doing', 'done', 'did', 'does']
HAVE_VERB_FORMS = ['has', 'have', 'had', 'having']

HEAD_AUX_TAGS = ['MD']
DEPENDENT_AUX_TAGS = ['IN', 'JJ', 'RB']

OBJECT_PRONOUNS = {'I': 'me', 'he': 'him', 'she': 'her', 'they': 'them',
                       'we': 'us', }