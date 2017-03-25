# -*- coding: utf-8 -*-
import requests
import json
# from google.appengine.ext import ndb
from pprint import pprint
from utils.data import Item
from API.api_utils import *
from API.order_menu import makeMainCB

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def get_menu(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/menu' % (namespace)
    res = requests.get(url)
    if (res.ok):
        return json.loads(res.content)
    else:
        return 'Error'

state = {'steps': []}


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


    if step[TYPE] == 'categ':
        return make_step_cat(menu["categories"], it_id)

    if step[TYPE] == 'item':
        return make_step_item(menu["items"], it_id)


def list_categories(categories, steps):
    res = []

    # pprint(categories)

    for cat in categories:
        cb = makeCBWithID('category', cat['info']['category_id'])
        res += [makeButton(cat['info']['title'], cb)]

    if len(steps) > 0:
        cb = makeEmptyCB('back')
        res += [makeButton(u'<- Назад', cb)]

    return {'buttons': res}


def list_items(items, steps):
    res = []

    for i in items:
        cb = makeCBWithID('item', i['id'])
        res += [makeButton(i['title'], cb)]

    if len(steps) > 0:
        cb = makeEmptyCB('back')
        res += [makeButton(u'<- Назад', cb)]

    return {'buttons': res}

def getItemsBySteps(menu, steps):
    first = True
    for step in steps:
        menu = make_step(menu, step, first)
        first = False

    return menu


def getCategoryLayout(chat_id, menu, steps):

    if len(steps) == 0:
        layout = list_categories(menu, steps)
        cb_order = makeMainCB()
        b = makeButton(u'Перейти к заказу', cb_order)
        layout['buttons'].append(b)
        layout['text'] = buildItemsString(items)
        return layout

    first = True
    for step in steps:
        menu = make_step(menu, step, first)
        first = False

    typelast = steps[-1][TYPE]

    if typelast == 'categ':
        if len(menu['categories']) != 0:
            layout = list_categories(menu['categories'], steps)
        else:
            layout = list_items(menu['items'], steps)
        return layout

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

def getItemLayout(item):
    layout = {}
    layout['img'] = item['pic']

    # cost = getCost(item)

    layout['text'] = itemDictToStr(item)

    buttons = []


    if len(item['group_modifiers']) > 0:
        opts = item['group_modifiers']
        for opt in opts:
            cb = makeCBWithID('option', opt['modifier_id'])
            b = makeButton(opt['title'], cb)

            buttons += [b]

    cb_plus = makeCountItemCB(1)
    b_plus = makeButton('+1', cb_plus)

    cb_minus = makeCountItemCB(-1)

    b_minus = makeButton('-1', cb_minus)

    buttons += [b_plus, b_minus]

    cb_add = makeEmptyCB('add')
    b_add = makeButton(u'Добавить в корзину', cb_add)
    buttons += [b_add]

    cb_back = makeEmptyCB('back')
    b_back = makeButton(u'<- Назад', cb_back)
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
    layout = {}
    buttons = []
    for i, ch in enumerate(choices):
        cost = ch['price']
        title = ch['title']
        name = u"{0} (+{1})".format(title, cost)

        cb = makeCBWithID('choice', ch['id'])

        button = makeButton(name, cb)

        buttons += [button]
    layout['buttons'] = buttons
    layout['text'] = itemDictToStr(item)

    return layout


def getChoiceIndex(choices, tofind):
    for i, ch in enumerate(choices):
        if ch['id'] == tofind:
            return i

          
def constructItemId(item):
    id = str(item['id'])
    opts = item['group_modifiers']
    for opt in opts:
        choices = opt['choices']
        for ch in choices:
            if ch['default']:
                id += '#{0}'.format(ch['id'])
    return id

def constructName(item):
    name = item['title']

    mods = []

    opts = item['group_modifiers']
    for opt in opts:
        choices = opt['choices']
        for ch in choices:
            if ch['default']:
                mods.append(unicode(ch['title']))

    if len(mods) > 0:
        m_string = ' ({0})'.format(', '.join(mods))
        name += m_string
    return name


def getContinueOrderLayout():
    cb_continue = makeCBWithID('category', None)
    button_continue = {'name': 'К меню', 'callback': cb_continue}
    cb_checkout = makeMainCB()
    button_checkout = {'name': 'Оформить заказ', 'callback': cb_checkout}

    return {'text': u'Товар добавлен в корзину!', 'buttons': [button_continue, button_checkout]}


def constructItem(item_dict):
    item_id = constructItemId(item_dict)
    item_name = constructName(item_dict)
    item_count = item_dict['count']
    item_price = getPrice(item_dict)
    item = Item(item_id,
                item_name,
                item_count,
                item_price)
    return item

def getMenuLayout(namespace, chat_id, callback=None):
    menu = get_menu(namespace)['menu']
    if callback == None:
        callback = {TYPE: 'category', 'id': None}

    cb_type = callback[TYPE]

    state = getStateByChatId(chat_id)

    items = loadOrder(chat_id)['items']

    if cb_type == 'category':
        steps = state['steps']
        if callback['id'] is not None:
            step = {'id': callback['id'], TYPE: 'categ'}
            state['steps'].append(step)
        layout = getCategoryLayout(chat_id, menu, steps)
        layout['text'] = buildItemsString(items)

    elif cb_type == 'item':
        step = {'id': callback['id'], TYPE: 'item'}
        state['steps'].append(step)
        item = getItemsBySteps(menu, state['steps'])
        item[u'count'] = 1
        layout = getItemLayout(item)

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
        layout = getItemLayout(item)

    elif cb_type == 'count':
        item = state['item']
        newcount = max(1, item['count'] + callback['val'])
        item['count'] = newcount
        layout = getItemLayout(item)

    elif cb_type == 'back':
        state['steps'] = state['steps'][:-1]
        state['item'] = None

        layout = getCategoryLayout(chat_id, menu, state['steps'])
        layout['text'] = buildItemsString(items)

    elif cb_type == 'add':
        order = loadOrder(chat_id)['items']
        item_dict = state['item']
        item = constructItem(item_dict)

        if item.id in order:
            item.count += order[item.id].count

        updateItem(item, chat_id)

        state = {'steps': []}
        # updateOrderStateByChatId(chat_id, order)
        layout = getContinueOrderLayout()
        layout['text'] = buildItemsString(items)


    saveState(chat_id, state)

    return layoutComplement(layout)




# namespace = 'slaviktest'
# chat_id = 1
#
# item = get_menu(namespace)['menu'][1]['items'][0]
#
# print(constructName(item))

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


