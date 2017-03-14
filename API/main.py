# -*- coding: utf-8 -*-
import requests
import json


def get_menu(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/menu' % (namespace)
    res = requests.get(url)
    if (res.ok):
        return json.loads(res.content)
    else:
        return 'Error'


def get_categories(namespace):
    menu = get_menu(namespace)['menu']
    categories = []

    for i in menu:
        categories.append(i['info']['title'])

    return categories


def get_items(namespace, category):
    menu = get_menu(namespace)['menu']

    items = []
    for i in menu:
        if i['info']['title'] == category:
            items = i['items']
            break

    res = []
    for i in items:
        res.append(i['title'])

    return res