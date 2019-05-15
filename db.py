from pymongo import MongoClient


# brew services start mongodb-community@4.0
def run_db():
    client = MongoClient('localhost', 27017)
    global db
    db = client.cached_dictionary


def get_collection_name(in_lang, out_lang): return in_lang + '_' + out_lang


def cache_add(data, _, in_lang, out_lang):
    print("adding to CACHE")
    db[get_collection_name(in_lang, out_lang)].insert_one(data)


def cache_get(head_word, in_lang, out_lang):
    return db[get_collection_name(in_lang, out_lang)].find_one({"results": {"$elemMatch": {"word": head_word}}})