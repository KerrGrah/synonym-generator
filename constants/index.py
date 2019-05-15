from datetime import datetime
from spacy.parts_of_speech import IDS as POS_IDS
import constants.dict_entities as DictEntity
import constants.data_paths as DataPath
import constants.file_paths as FilePath
import constants.lexical_categories as LexicalCategory
import constants.lang as Lang

L_ONE = Lang.ES
L_TWO = Lang.EN

USE_LOCAL_DICT = True
USE_REMOTE_DICT = True
UPDATE_LOCAL_DICT = USE_LOCAL_DICT and True

ACCEPT_REGION = 'Spain'
ACCEPT_POS = LexicalCategory.NOUN  # None

OUTPUT_FOLDER = 'output-{}-{} {}'.format(L_ONE, L_TWO, datetime.now().strftime("%d-%m-%y - %H:%M:%S"))

# e.g. free usage limit one call per second
API_TIMEOUT = 1.01

# maps spacy part of speech enum to oxford api equivalent
MAP_POS_TO_LEXICAL_CATEGORY = {
    POS_IDS["ADJ"]: LexicalCategory.ADJECTIVE,
    POS_IDS["NOUN"]: LexicalCategory.NOUN,
    POS_IDS["ADV"]: LexicalCategory.ADVERB,
    POS_IDS["VERB"]: LexicalCategory.VERB
}
