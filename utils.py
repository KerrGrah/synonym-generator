import codecs
import os
import json
import time
from bson.json_util import _json_convert
from difflib import get_close_matches
from functools import reduce
import es_core_news_sm
from constants.index import *

nlp = es_core_news_sm.load()


def write_to_file(file_path, data):
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        json.dump(_json_convert(data), f, ensure_ascii=False)


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def update_file(f_p, data):
    file_path = OUTPUT_FOLDER + '/' + f_p
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as previous:
            new_data = json.load(previous)
            new_data.update(data)
            data = new_data
    write_to_file(file_path, data)


def deep_get(dictionary, path, default=None):
    return reduce(lambda d, key: d.get(key) if isinstance(d, dict) else d[int(key)] if isinstance(d, list) else default,
                  path.split("."),
                  dictionary)


def get_lemma(word):
    return nlp(word)[0].lemma_


def get_pos(word):
    return MAP_POS_TO_LEXICAL_CATEGORY.get(nlp(word)[0].pos)


# e.g. exclude "entrenadora" if results_list already contains "entrenador" (lemma filter),
# or exclude "birrete" if already contains "birreta" (close match filter)
def already_contains_similar(word, results_list):
    if get_close_matches(word, results_list, 1, 0.8):
        return True

    new_lemma = get_lemma(word)
    for w in results_list:
        if new_lemma == get_lemma(w):
            return True

    return False


def raise_exception(msg, data=None):
    raise Exception(msg, data)


def get_error_message(response):
    return 'remote error {code}, \n {message}'.format(code=response.status_code,
                                                      message=response.content.decode("utf-8"))


def reject(translation, agg_translations, l1_word, l2_word):
    update_file(FilePath.REJECTED_TRANS_LOG,
                {"l2_word": l2_word, "l1_word": l1_word, "rejected_translation": translation,
                 "agg_translations": agg_translations})


last_request_time = 0


def sleep_remote():
    global last_request_time
    sleep_duration = max(API_TIMEOUT - (time.time() - last_request_time), 0)
    time.sleep(sleep_duration)
    last_request_time = time.time()

