# -*- coding: utf-8 -*-
import requests
import json
# from google.appengine.ext import ndb
from pprint import pprint
from utils.data import Item, getMenuStateByChatId, updateMenuStateByChatId
from utils.data import getOrderStateByChatId, updateOrderStateByChatId
from API.api_utils import *

def get_menu(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/menu' % (namespace)
    res = requests.get(url)
    if (res.ok):
        return json.loads(res.content)
    else:
        return 'Error'

# state = {'steps': []}

def makeItemMenuCB():
    cb = {}
    cb['chat'] = ITEM_CHAT
    return cb

def makeEmptyCB(type):
    cb = makeItemMenuCB()
    cb['type'] = type
    return cb

def makeCBWithID(type, id):
    cb = makeEmptyCB(type)
    cb['id'] = id
    return cb

def makeCountCB(val):
    cb = makeEmptyCB('count')
    cb['val'] = val
    return cb

def getStateByChatId(chat_id):
    return json.loads(getMenuStateByChatId(chat_id))

def saveState(chat_id, st):
    updateMenuStateByChatId(chat_id, st)

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
        cb = makeCBWithID('category', cat['info']['category_id'])
        res += [makeButton(cat['info']['title'], cb, ITEM_CHAT)]

    if len(steps) > 0:
        cb = makeEmptyCB('back')
        res += [makeButton(u'Назад', cb, ITEM_CHAT)]

    return {'buttons': res}


def list_items(items, steps):
    res = []

    for i in items:
        cb = makeCBWithID('item', i['id'])
        res += [makeButton(i['title'], cb)]

    if len(steps) > 0:
        cb = makeEmptyCB('back')
        res += [makeButton(u'Назад', cb)]

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

def getPrice(item):
    cost = item['price']

    for mod in item['group_modifiers']:
        opts = mod['choices']
        for opt in opts:
            if opt['default']:
                cost += opt['price']

    return cost

def getCost(item):
    price = getPrice(item)
    return price * item[u'count']



def getItemLayout(steps, item):
    layout = {}
    layout['img'] = item['pic']

    cost = getCost(item)

    layout['text'] = u'{0} ({1})\nЦена: {2}'.format(item['title'], item['count'], cost)

    buttons = []


    if len(item['group_modifiers']) > 0:
        opts = item['group_modifiers']
        for opt in opts:
            cb = makeCBWithID('option', opt['modifier_id'])
            b = makeButton(opt['title'], cb)

            buttons += [b]

    cb_plus = makeCountCB(1)
    b_plus = makeButton('+1', cb_plus)

    cb_minus = makeCountCB(-1)
    b_minus = makeButton('-1', cb_minus)

    buttons += [b_plus, b_minus]

    cb_add = makeEmptyCB('add')
    b_add = makeButton(u'Добавить в корзину', cb_add)
    buttons += [b_add]

    cb_back = {}
    cb_back['type'] = 'back'
    b_back = makeButton(u'Назад', cb_back)
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

        cb = makeCBWithID('choice', ch['id'])

        button = makeButton(name, cb)

        buttons += [button]

    return {'buttons': buttons}


def getChoiceIndex(choices, tofind):
    for i, ch in enumerate(choices):
        if ch['id'] == tofind:
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


    elif cb_type == 'item':
        step = {'id': callback['id'], 'type': 'item'}
        state['steps'].append(step)
        item = getItemsBySteps(menu, state['steps'])
        item[u'count'] = 1
        layout = getItemLayout(state['steps'], item)

        state['item'] = item

    elif cb_type == 'option':
        state['option'] = callback['id']
        layout = getOptionLayout(state['item'], state['option'])

    elif cb_type == 'choice':
        item = state['item']
        choices, opt_ind = getChoicesJson(item, state['option'])
        ch_ind = getChoiceIndex(choices, callback['id'])

        item['group_modifiers'][opt_ind]['choices'] = updateChoices(choices, ch_ind)

        state['item'] = item
        state['choice'] = None
        layout = getItemLayout(state['steps'], item)

    elif cb_type == 'count':
        item = state['item']
        newcount = max(1, item['count'] + callback['val'])
        item['count'] = newcount
        layout = getItemLayout(state['steps'], item)

    elif cb_type == 'back':
        state['steps'] = state['steps'][:-1]
        state['item'] = None

        layout = getCategoryLayout(menu, state['steps'])


    elif cb_type == 'add':
        # addToCart(history['item']) # FOR PLATON
        order = getOrderStateByChatId(chat_id)
        item_dict = state['item']
        item_id = item_dict['id']
        item_name = item_dict['title']
        item_count = item_dict['count']
        item_price = getPrice(item_dict)
        if item_id in order:
            order[item_id].count += item_count
        else:
            item = Item(item_id,
                    item_name,
                    item_count,
                    item_price)
            order[item_id] = item

        updateOrderStateByChatId(chat_id, order)
        layout = {'text': u'Товар добавлен в корзину!'}

    saveState(chat_id, state)

    # pprint(layout)
    return layoutComplement(layout)



#
# namespace = 'slaviktest'
# chat_id = 1
#
# bs1 = getMenuLayout(namespace, chat_id)['buttons']
# bs2 = getMenuLayout(namespace, chat_id, bs1[1]['callback'])['buttons']
# bs3 = getMenuLayout(namespace, chat_id, bs2[0]['callback'])['buttons']
# bs4 = getMenuLayout(namespace, chat_id, bs3[1]['callback'])['buttons']
# bs5 = getMenuLayout(namespace, chat_id, bs4[1]['callback'])['buttons']

# pprint(bs3[1])
#
# pprint(getMenuLayout(namespace, chat_id, bs4[1]['callback']))
#
# pprint(getMenuLayout(namespace, chat_id, bs3[0]['callback']))
#
# pprint(state)