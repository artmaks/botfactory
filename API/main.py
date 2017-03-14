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


# def follow_path(menu_json, path=None):
#     if path == None:
#         path = '[]'
#     #jsd = json.JSONDecoder()
#     steps = json.loads(path)
#
#     print steps

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

    # pprint(categories)

    for cat in categories:
        step = {'name': cat['info']['title'], 'type': 'categ'}
        cb = {}
        cb['type'] = 'category'
        cb['steps'] = steps + [step]
        res += [{'name': cat['info']['title'], 'callback': cb}]

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


    if len(item['group_modifiers']) > 0:
        opts = item['group_modifiers']
        for opt in opts:
            b = {}
            b['name'] = opt['title']

            cb = {}
            cb['type'] = 'option'
            cb['steps'] = steps
            cb['item'] = item
            cb['option'] = opt['title']
            b['callback'] = cb

            buttons += [b]

    cb_add = {}
    cb_add['type'] = 'add'
    cb_add['item'] = item
    b_add = {}
    b_add['name'] = 'Add to cart'
    b_add['callback'] = cb_add
    buttons += [b_add]

    cb_back = {}
    cb_back['type'] = 'category'
    cb_back['steps'] = steps
    b_back = {}
    b_back['name'] = 'Back'
    b_back['callback'] = cb_back
    buttons += [b_back]

    layout['buttons'] = buttons

    return layout

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

    return choices #dgdfg

def getOptionLayout(steps, item, option_name):
    choices = getChoicesJson(item, option_name)

    buttons = []
    for i, ch in enumerate(choices):
        cost = ch['price']
        title = ch['title']
        name = u"{0} (+{1})".format(title, cost)

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
        return getOptionLayout(history['steps'], history['item'], history['option'])

    if type == 'add':
        # addToCart(history['item']) # FOR PLATON
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


# spath = u'[{"name": "Кофе", "type": "categ"}, {"name": "Капучино", "type": "item"}]'
# steps = json.loads(spath)
# # pprint(steps)
#
# menu = getMenu('slaviktest')['menu']
# step1 = make_step(menu, steps[0], True)
# step2 = make_step(step1, steps[1], False)
# pprint(getMenuItems('slaviktest', steps[:1]))
# namespace = 'slaviktest'

# history = {}
# history = {'type': 'category', 'steps': []}
# history = {'steps': [{'name': u'\u041a\u043e\u0444\u0435','type': 'categ'}],'type': 'category'}
# history = {'item': {u'carbohydrate': 0.0,
#                                     u'description': u'Средний по крепости напиток на основе эспрессо, с добавлением вспененного теплого молока и мягкой молочной пенкой.',
#                                     u'fat': 0.0,
#                                     u'fiber': 0.0,
#                                     u'group_modifiers': [{u'choices': [{u'default': None,
#                                                                         u'id': u'10',
#                                                                         u'order': 189,
#                                                                         u'price': 50.0,
#                                                                         u'prices': [],
#                                                                         u'title': u'Средний'},
#                                                                        {u'default': True,
#                                                                         u'id': u'183',
#                                                                         u'order': 156,
#                                                                         u'price': 0.0,
#                                                                         u'prices': [],
#                                                                         u'title': u'Мелкий'},
#                                                                        {u'default': None,
#                                                                         u'id': u'240',
#                                                                         u'order': 262,
#                                                                         u'price': 100.0,
#                                                                         u'prices': [],
#                                                                         u'title': u'Огромный'}],
#                                                           u'max_value': 1,
#                                                           u'min_value': 1,
#                                                           u'modifier_id': u'5652383656837120',
#                                                           u'order': 133,
#                                                           u'required': True,
#                                                           u'title': u'Объем'}],
#                                     u'icon': u'http://lh3.googleusercontent.com/32UZvmrHtPiyZdAxWXTblKy78iMttXnTacVuD1a7aE5skQ4MJP1xjGSlvGB5ZQCxtEVfHq1B9G2t5C6-jmD-Mk135BsdSgJXoQOmsU4FwtZ5SX-y=s128',
#                                     u'id': u'5091364022779904',
#                                     u'kal': 0,
#                                     u'order': 55,
#                                     u'pic': u'http://lh3.googleusercontent.com/H6k2FeiAtnRwaEH-XSPj-JEZ57U9AnLwt1Gj9cufoE4VwY43l5iAgRPaprX5LCar2GJUd7r5wamdzvxEbEejSN8lzrgkgibk9yrMI_Bk35k9b8k=s960',
#                                     u'pic_background': u'FFFFFF',
#                                     u'pic_resize': 0,
#                                     u'price': 120.0,
#                                     u'prices': [],
#                                     u'restrictions': {u'venues': []},
#                                     u'single_modifiers': [],
#                                     u'title': u'Капучино',
#                                     u'volume': 0.0,
#                                     u'weight': 0.0},
#                            'steps': [{'name': u'Кофе',
#                                       'type': 'categ'},
#                                      {'name': u'Капучино',
#                                       'type': 'item'}],
#                            'type': 'item'}
#
# history = {'item': {u'carbohydrate': 0.0,
#                                     u'description': u'\u0421\u0440\u0435\u0434\u043d\u0438\u0439 \u043f\u043e \u043a\u0440\u0435\u043f\u043e\u0441\u0442\u0438 \u043d\u0430\u043f\u0438\u0442\u043e\u043a \u043d\u0430 \u043e\u0441\u043d\u043e\u0432\u0435 \u044d\u0441\u043f\u0440\u0435\u0441\u0441\u043e, \u0441 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435\u043c \u0432\u0441\u043f\u0435\u043d\u0435\u043d\u043d\u043e\u0433\u043e \u0442\u0435\u043f\u043b\u043e\u0433\u043e \u043c\u043e\u043b\u043e\u043a\u0430 \u0438 \u043c\u044f\u0433\u043a\u043e\u0439 \u043c\u043e\u043b\u043e\u0447\u043d\u043e\u0439 \u043f\u0435\u043d\u043a\u043e\u0439.',
#                                     u'fat': 0.0,
#                                     u'fiber': 0.0,
#                                     u'group_modifiers': [{u'choices': [{u'default': None,
#                                                                         u'id': u'10',
#                                                                         u'order': 189,
#                                                                         u'price': 50.0,
#                                                                         u'prices': [],
#                                                                         u'title': u'\u0421\u0440\u0435\u0434\u043d\u0438\u0439'},
#                                                                        {u'default': True,
#                                                                         u'id': u'183',
#                                                                         u'order': 156,
#                                                                         u'price': 0.0,
#                                                                         u'prices': [],
#                                                                         u'title': u'\u041c\u0435\u043b\u043a\u0438\u0439'},
#                                                                        {u'default': None,
#                                                                         u'id': u'240',
#                                                                         u'order': 262,
#                                                                         u'price': 100.0,
#                                                                         u'prices': [],
#                                                                         u'title': u'\u041e\u0433\u0440\u043e\u043c\u043d\u044b\u0439'}],
#                                                           u'max_value': 1,
#                                                           u'min_value': 1,
#                                                           u'modifier_id': u'5652383656837120',
#                                                           u'order': 133,
#                                                           u'required': True,
#                                                           u'title': u'\u041e\u0431\u044a\u0435\u043c'}],
#                                     u'icon': u'http://lh3.googleusercontent.com/32UZvmrHtPiyZdAxWXTblKy78iMttXnTacVuD1a7aE5skQ4MJP1xjGSlvGB5ZQCxtEVfHq1B9G2t5C6-jmD-Mk135BsdSgJXoQOmsU4FwtZ5SX-y=s128',
#                                     u'id': u'5091364022779904',
#                                     u'kal': 0,
#                                     u'order': 55,
#                                     u'pic': u'http://lh3.googleusercontent.com/H6k2FeiAtnRwaEH-XSPj-JEZ57U9AnLwt1Gj9cufoE4VwY43l5iAgRPaprX5LCar2GJUd7r5wamdzvxEbEejSN8lzrgkgibk9yrMI_Bk35k9b8k=s960',
#                                     u'pic_background': u'FFFFFF',
#                                     u'pic_resize': 0,
#                                     u'price': 120.0,
#                                     u'prices': [],
#                                     u'restrictions': {u'venues': []},
#                                     u'single_modifiers': [],
#                                     u'title': u'\u041a\u0430\u043f\u0443\u0447\u0438\u043d\u043e',
#                                     u'volume': 0.0,
#                                     u'weight': 0.0},
#                            'option': u'\u041e\u0431\u044a\u0435\u043c',
#                            'steps': [{'name': u'\u041a\u043e\u0444\u0435',
#                                       'type': 'categ'},
#                                      {'name': u'\u041a\u0430\u043f\u0443\u0447\u0438\u043d\u043e',
#                                       'type': 'item'}],
#                            'type': 'option'}
# # pprint(getMenu('slaviktest'))
# pprint(getMenuLayout(namespace, history))

# print('ывпывпвыпывп')
# print(u'пывпывппывп')