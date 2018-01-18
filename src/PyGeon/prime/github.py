import requests
import pandas as pd

GHURL = 'https://api.github.com'


def get_user_details(name):
    url = GHURL + "/users/" + name
    r = requests.get(url)
    details = r.json()
    if 'message' in details:
        return False
    keys = ['location', 'name', 'email', 'public_repos', 'bio',
            'repos_url', 'html_url']
    reduced = dict((k, details[k]) for k in keys)
    lang_dict, x = None, None
    if reduced['public_repos']:
        lang_dict = get_lang_dict(reduced['repos_url'])
        x = pd.Series(lang_dict)
        x = x[x / x.sum() > 0.1].sort_values(ascending=False)
    return reduced, x, lang_dict


def get_lang_dict(url):

    r = requests.get(url)
    counter = {}
    score = {False: 3, True: 1}
    for i in r.json():
        lang = i['language']
        if lang is not None:
            counter[lang] = counter.get(lang, 0) + score[i['fork']]
    return counter


get_user_details('buckyroberts')
