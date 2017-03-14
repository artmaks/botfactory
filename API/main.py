# -*- coding: utf-8 -*-
import requests
import json

def getMenu(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/menu' % (namespace)
    res = requests.get(url)
    if (res.ok):
        return json.loads(res.content)
    else:
        return 'Error'

def getCategories(namespace):
    menu = getMenu(namespace)['menu']
    categories = []

    for i in menu:
        categories.append(i['info']['title'])

    return categories

def getItems(namespace, category):
    menu = getMenu(namespace)['menu']

    items = []
    for i in menu:
        if i['info']['title'] == category:
            items = i['items']
            break

    res = []
    for i in items:
        res.append(i['title'])

    return res