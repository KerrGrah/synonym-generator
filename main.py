from remote import make_lookup
from db import *
from utils import *

"""
Takes a JSON list of words and generates "true" synonyms i.e. words that are nearly identical in meaning 
(as opposed to thesaurus synonyms).

Example input list created by taking a list of Spanish words from EsPal corpus
https://www.bcbl.eu/databases/espal/ with concreteness parameter >= 5.3 and
merging with a list taken from the MultiPic database https://www.bcbl.eu/databases/multipic/.
Results were used to create stimuli for a study.
"""


def main():
    create_dir(OUTPUT_FOLDER)

    if USE_LOCAL_DICT or UPDATE_LOCAL_DICT:
        run_db()

    with open(FilePath.INPUT_LIST) as source_file:
        source = json.load(source_file)

        for l1_word in source:

            match_for_pos = ACCEPT_POS or get_pos(l1_word) or LexicalCategory.NOUN

            l2_word = do_translation_to_lang_2(l1_word, match_for_pos)

            if l2_word:
                do_translation_back_to_lang_1(l1_word, match_for_pos, l2_word)



def do_translation_to_lang_2(l1_word, match_for_pos):
    do_lookup = make_lookup(L_ONE, L_TWO)
    try:
        return parse_response(do_lookup(l1_word), match_for_pos, get_single_translation)

    except Exception as e:
        update_file(FilePath.L1_TO_L2_ERROR_LOG, {l1_word: {"exception": e.args[0], "data": e.args[1]}})


def do_translation_back_to_lang_1(l1_word, match_for_pos, l2_word):
    do_lookup = make_lookup(L_TWO, L_ONE)
    find_translation = make_get_translations_list(l1_word, l2_word)
    try:
        translations = parse_response(do_lookup(l2_word), match_for_pos, find_translation)

        if translations:
            # only one word, log
            if len(translations) == 1:
                update_file(FilePath.NO_SYNONYM, {l1_word: {l2_word: translations}})
            # possibly useful result
            elif len(translations) > 1:
                update_file(FilePath.RESULTS, {l1_word: translations})

        # no translation, log
        else:
            raise_exception("No translation found in parse")
    except Exception as e:
        print(e)
        update_file(FilePath.L2_TO_L1_ERROR_LOG,
                    {l1_word: {"l2_word": l2_word, "exception": e.args[0], "data": e.args[1]}})


# returns first entry with matching lexical category (part of speech).
# can set desired part of speech with ACCEPT_POS, eg "Noun", or will match for l1_word POS
def parse_response(lookup_result, match_for_pos, get_translation):
    lexical_entries = deep_get(lookup_result, DataPath.LEXICAL_ENTRIES)
    for entry in lexical_entries:
        if entry[DictEntity.LEXICAL_CATEGORY] == match_for_pos:

            found_results = get_translation(deep_get(entry, DataPath.SENSES))
            if found_results:
                return found_results

    raise_exception('parse response failed (likely no {} found)'.format(match_for_pos), lexical_entries)


def get_single_translation(senses):
    for sense in senses:
        if DictEntity.TRANSLATIONS in sense:
            return deep_get(sense, DataPath.TRANSLATION_TEXT)

        elif DictEntity.SUBSENSES in sense:
            resolved = get_single_translation(sense[DictEntity.SUBSENSES])
            return resolved if resolved else None


def make_get_translations_list(l1_word, l2_word):
    def get_translations_list(senses):
        for sense in senses:
            results = []
            if DictEntity.TRANSLATIONS in sense:
                for translation in sense[DictEntity.TRANSLATIONS]:
                    if is_useful_translation(translation, results, l1_word, l2_word):
                        results.append(translation[DictEntity.TEXT])
                if l1_word.lower() in [w.lower() for w in results]:
                    return results

            elif DictEntity.SUBSENSES in sense:
                resolved = get_translations_list(sense[DictEntity.SUBSENSES])
                return resolved if resolved else None

    return get_translations_list


def is_useful_translation(translation, results, l1_word, l2_word):
    reject_conditions = [
        # 1. reject translations that are grammatical notes e.g. 'before noun'
        deep_get(translation, DataPath.NOTES_TYPE) == DictEntity.GRAMMATICAL_NOTE,
        # 2. reject regional translations that are not the "accepted" region
        DictEntity.REGIONS in translation and ACCEPT_REGION not in translation[DictEntity.REGIONS],
        # 3. reject semi-duplicates
        already_contains_similar(translation[DictEntity.TEXT],
                                 results)
    ]

    if any(reject_conditions):
        return reject(translation, results, l1_word, l2_word)
    else:
        return True


main()

# TODO look for crossreferences but with no translations eg "tyre" -> redirects "tire"
