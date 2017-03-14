# -*- coding: utf-8 -*-
import requests
import json
from pprint import pprint


def getMenu(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/menu' % (namespace)
    res = requests.get(url)
    if (res.ok):
        return json.loads(res.content)
    else:
        return 'Error'


def follow_path(menu_json, path=None):
    if path == None:
        path = '[]'
    #jsd = json.JSONDecoder()
    steps = json.loads(path)

    print steps

def make_step_cat(catlist, name):
    for entry in catlist:
        if entry['info']['title'] == name:
            return entry

def make_step_item(itemlist, name):
    for entry in itemlist:
        if entry['title'] == name:
            return entry

def make_step(menu, step, first=False):

    name = step['name']

    if first:
        return make_step_cat(menu, name)


    if step['type'] == 'categ':
        return make_step_cat(menu["categories"], name)

    if step['type'] == 'item':
        return make_step_item(menu["items"], name)


def list_categories(categories, steps):
    res = []

    for cat in categories:
        step = {'name': cat['title'], 'type': 'categ'}
        cb = {}
        cb['type'] = 'category'
        cb['steps'] = steps + [step]
        res += [{'name': cat['title'], 'callback': cb}]

    if len(steps) > 0:
        cb = {}
        cb['type'] = 'category'
        cb['steps'] = steps[:-1]
        res += [{'name': u'Назад', 'callback': cb}]

    return {'buttons': res}


def list_items(items, steps):
    res = []

    for i in items:
        step = {'name': i['title'], 'type': 'item'}
        cb = {}
        cb['type'] = 'item'
        cb['steps']  = steps + [step]
        cb['item'] = i

        res += [{'name': i['title'], 'callback': cb}]

    if len(steps) > 0:
        cb = {}
        cb['type'] = 'category'
        cb['steps'] = steps[:-1]
        res += [{'name': u'Назад', 'callback': cb}]

    return {'buttons': res}

def getCategoryItems(menu, steps):
    if len(steps) == 0:
        return list_categories(menu, steps)

    first = True
    for step in steps:
        menu = make_step(menu, step, first)
        first = False

    typelast = steps[-1]['type']

    if typelast == 'categ':
        if len(menu['categories']) != 0:
            return list_categories(menu['categories'])
        else:
            return list_items(menu['items'], steps)

def getCost(item):
    cost = item['price']

    if 'choices' in item['group_modifiers']:
        opts = item['group_modifiers']['choices']
        for opt in opts:
            if opt['default']:
                cost += opt['price']

    return cost



def getItemLayout(steps, item):
    layout = {}
    layout['img'] = item['pic']

    cost = getCost(item)

    layout['text'] = 'Цена: {0}'.format(cost)

    buttons = []

    if 'choices' in item['group_modifiers']:
        opts = item['group_modifiers']['choices']
        for opt in opts:
            b = {}
            b['name'] = opt['title']

            cb = {}
            cb['type'] = 'option'
            cb['steps'] = steps
            cb['item'] = item
            cb['option'] = opt['title']
            b['callback'] = cb

            buttons += b

    cb_add = {}
    cb_add['type'] = 'add'
    cb_add['item'] = item
    b_add = {}
    b_add['name'] = 'Add to cart'
    b_add['callback'] = cb_add
    buttons += b_add

    cb_back = {}
    cb_back['type'] = 'category'
    cb_back['steps'] = steps
    b_back = {}
    b_back['name'] = 'Back'
    b_back['callback'] = cb_back
    buttons += b_back

    layout['buttons'] = buttons

    return buttons

def getChoicesJson(item, option_name):
    modifiers = item['group_modifiers']

    for mod in modifiers:
        if mod['title'] == option_name:
            return mod['choices']

def updateChoices(choices, toSelect):
    for i, ch in enumerate(choices):
        if i == toSelect:
            choices[i] = True
        else:
            choices[i] = False

    return choices

def getOptionLayout(steps, item, option_name):
    choices = getChoicesJson(item, option_name)

    buttons = []
    for i, ch in enumerate(choices):
        cost = ch['price']
        title = ch['title']
        name = "{0} (+{1})".format(title, cost)

        cb = {}
        item['group_modifiers']['choices'] = updateChoices(choices, i)
        cb['type'] = 'item'
        cb['steps'] = steps
        cb['item'] = item

        button = {}
        button['name'] = name
        button['callback'] = cb

        buttons += button

    return {'buttons': buttons}

def getMenuLayout(namespace, history):
    menu = getMenu(namespace)['menu']

    type = history['type']

    if type == 'category':
        steps = history['steps']
        return getCategoryItems(menu, steps)

    if type == 'item':
        return getItemLayout(history['steps'], history['item'])

    if type == 'option':
        getOptionLayout(history['steps'], history['item'], history['option'])

    if type == 'add':
        addToCart(history['item']) # FOR PLATON
        return {'text': 'Added!'}


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


spath = u'[{"name": "Кофе", "type": "categ"}, {"name": "Капучино", "type": "item"}]'
steps = json.loads(spath)
# pprint(steps)

menu = getMenu('slaviktest')['menu']
step1 = make_step(menu, steps[0], True)
step2 = make_step(step1, steps[1], False)
pprint(getMenuItems('slaviktest', steps[:1]))

# print('ывпывпвыпывп')
# print(u'пывпывппывп')