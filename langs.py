import os
import json


def getlanglist(path_to_langs):
    langfiles = os.listdir(path_to_langs)
    langlist = []
    for langfile in langfiles:
        with open(path_to_langs + langfile, 'r', encoding='utf-8') as f:
            values = json.loads(f.read())
            langlist.append([langfile.split('.')[0], values['_header']['original_name'], values['_header']['language']])
    return langlist

def getlanguage(langfile):
    with open(langfile, 'r', encoding='utf-8') as f:
        values = json.loads(f.read())
    return values
