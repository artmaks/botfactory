# -*- coding: utf-8 -*-
import requests
import json
from google.appengine.ext import ndb
from pprint import pprint
from models.Models import *
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.data import *


def get_menu(namespace):
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

state = {'steps': []}

def getStateByChatId(chat_id):
    return state

def saveState(st):
    global state
    state = st

def make_step_cat(catlist, c_id):
    for entry in catlist:
        if entry['info']['category_id'] == c_id:
            return entry

def make_step_item(itemlist, i_id):
    for entry in itemlist:
        if entry['id'] == i_id:
            return entry

def make_step(menu, step, first=False):

    it_id = step['id']

    if first:
        return make_step_cat(menu, it_id)


    if step['type'] == 'categ':
        return make_step_cat(menu["categories"], it_id)

    if step['type'] == 'item':
        return make_step_item(menu["items"], it_id)


def list_categories(categories, steps):
    res = []

    # pprint(categories)

    for cat in categories:
        cb = {}
        cb['type'] = 'category'
        cb['id'] = cat['info']['category_id']
        # pprint([{'name': cat['info']['title'], 'callback': cb}])
        res += [{'name': cat['info']['title'], 'callback': cb}]

    if len(steps) > 0:
        cb = {}
        cb['type'] = 'back'
        res += [{'name': u'Назад', 'callback': cb}]

    return {'buttons': res}


def list_items(items, steps):
    res = []

    for i in items:
        cb = {}
        cb['type'] = 'item'
        cb['id'] = i['id']
        res += [{'name': i['title'], 'callback': cb}]

    if len(steps) > 0:
        cb = {}
        cb['type'] = 'back'
        res += [{'name': u'Назад', 'callback': cb}]

    return {'buttons': res}

def getItemsBySteps(menu, steps):
    first = True
    for step in steps:
        menu = make_step(menu, step, first)
        first = False

    return menu


def getCategoryLayout(menu, steps):

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
            cb['id'] = opt['modifier_id']
            b['callback'] = cb

            buttons += [b]

    cb_add = {}
    cb_add['type'] = 'add'
    b_add = {}
    b_add['name'] = 'Add to cart'
    b_add['callback'] = cb_add
    buttons += [b_add]

    cb_back = {}
    cb_back['type'] = 'back'
    b_back = {}
    b_back['name'] = 'Back'
    b_back['callback'] = cb_back
    buttons += [b_back]

    layout['buttons'] = buttons

    return layout

def getChoicesJson(item, option_name):
    modifiers = item['group_modifiers']

    for i, mod in enumerate(modifiers):
        if mod['modifier_id'] == option_name:
            return mod['choices'], i

def updateChoices(choices, toSelect):
    for i, ch in enumerate(choices):
        if i == toSelect:
            choices[i]['default'] = True
        else:
            choices[i]['default'] = False

    return choices




def getOptionLayout(item, option_name):
    # pprint(getChoicesJson(item, option_name))
    choices, opt_ind = getChoicesJson(item, option_name)
    buttons = []
    for i, ch in enumerate(choices):
        cost = ch['price']
        title = ch['title']
        name = u"{0} (+{1})".format(title, cost)
        #
        cb = {}
        # item['group_modifiers'][opt_ind]['choices'] = updateChoices(choices, i)
        cb['type'] = 'choice'
        cb['id'] = ch['id']

        button = {}
        button['name'] = name
        button['callback'] = cb

        buttons += [button]

    return {'buttons': buttons}

def layoutComplement(layout):
    if 'buttons' not in layout:
        layout['buttons'] = []

    if 'img' not in layout:
        layout['img'] = None

    if 'text' not in layout:
        layout['text'] = None

    return layout

def getChoiceIndex(choices, tofind):
    for i, ch in enumerate(choices):
        if ch['title'] == tofind:
            return i

def getMenuLayout(namespace, chat_id, callback=None):
    menu = get_menu(namespace)['menu']
    if callback == None:
        callback = {'type': 'category', 'id': None}

    cb_type = callback['type']
    state = getStateByChatId(chat_id)

    if cb_type == 'category':
        steps = state['steps']
        if callback['id'] is not None:
            step = {'id': callback['id'], 'type': 'categ'}
            state['steps'].append(step)
        layout =  getCategoryLayout(menu, steps)


    if cb_type == 'item':
        step = {'id': callback['id'], 'type': 'item'}
        state['steps'].append(step)
        item = getItemsBySteps(menu, state['steps'])
        layout = getItemLayout(state['steps'], item)

        state['item'] = item

    if cb_type == 'option':
        state['option'] = callback['id']
        layout = getOptionLayout(state['item'], state['option'])

    if cb_type == 'choice':
        item = state['item']
        choices, opt_ind = getChoicesJson(item, state['option'])
        ch_ind = getChoiceIndex(choices, callback['id'])
        item['group_modifiers'][opt_ind]['choices'] = updateChoices(choices, ch_ind)

        state['item'] = item
        state['choice'] = None
        layout = getItemLayout(state['steps'], item)

    if cb_type == 'back':
        state['steps'] = state['steps'][:-1]
        state['item'] = None

        layout = getCategoryLayout(menu, state['steps'])

    if cb_type == 'add':
        item = state['item']
        order = getOrderByChatId(chat_id)
        new_item = OrderItem(parent=order.key, name='name', content="asd", count=1)
        new_item.put()
        layout = {'text': 'Added!'}


    saveState(state)
    # pprint(layout)
    return layoutComplement(layout)


def getCategories(namespace):
    menu = get_menu(namespace)['menu']
    categories = []

    for i in menu:
        categories.append(i['info']['title'])

    return categories


def getItems(namespace, category):
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



# namespace = 'slaviktest'
# chat_id = 1
#
# bs1 = getMenuLayout(namespace, chat_id)['buttons']
#
#
# # pprint(bs1)
# bs2 = getMenuLayout(namespace, chat_id, bs1[1]['callback'])['buttons']
# bs3 = getMenuLayout(namespace, chat_id, bs2[0]['callback'])['buttons']
# bs4 = getMenuLayout(namespace, chat_id, bs3[0]['callback'])['buttons']
# bs5 = getMenuLayout(namespace, chat_id, bs4[0]['callback'])['buttons']
# pprint(bs5)
#
# pprint(getMenuLayout(namespace, chat_id, bs3[0]['callback']))
#
# pprint(state)

