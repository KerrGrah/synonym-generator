import requests
from db import *
from api_keys import *
from utils import *


def get_url(head_word, from_lang, to_lang):
    return "https://od-api.oxforddictionaries.com/api/v1/entries/{from_lang}/{head_word}/translations={to_lang}".format(
        head_word=head_word, from_lang=from_lang, to_lang=to_lang)


def remote_lookup(*args):
    sleep_remote()

    url = get_url(*args)
    response = requests.get(url, headers={'app_id': app_id, "app_key": api_key})

    if response.ok:

        data = response.json()

        if UPDATE_LOCAL_DICT:
            cache_add(data, *args)

        return data

    raise_exception(get_error_message(response))


def make_lookup(*args):
    def lookup(lookup_word): return USE_LOCAL_DICT and cache_get(lookup_word, *args) \
                                    or USE_REMOTE_DICT and remote_lookup(lookup_word, *args) \
                                    or raise_exception('look up failed', args)

    return lookup
