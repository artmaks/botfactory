# -*- coding: utf-8 -*-
from pprint import pprint
# from API.main import makeButton, layoutComplement
# encoding=utf8
import sys
from API.api_utils import *

#

reload(sys)
sys.setdefaultencoding('utf8')
# ======================= STUBS FOR LOGIC TESTING ==========================

# Stub class to be replaced by model in Models.p




# ========================= (supposed to be) PRODUCTION CODE ======================

# callback['type'] = 'main' | 'proc'(proceed) | 'clear' | 'edit' | 'item' | 'count' | 'remove'



def emptyOrderLayout():
    layout = {}
    layout['buttons'] = []
    layout['text'] = u"Ваш заказ пуст."

    return layout


def orderLayout(order):
    layout = {}
    layout['text'] = buildItemsString(order)

    buttons = []

    proceed_cb = makeMoveCallback('addr')
    proceed_button = makeButton(u"Подтвердить", proceed_cb)
    buttons.append(proceed_button)

    edit_cb = makeEditCB()
    edit_button = makeButton(u"Изменить заказ", edit_cb)
    buttons.append(edit_button)

    clear_cb = makeClearCB()
    clear_button = makeButton(u"Очистить заказ", clear_cb)
    buttons.append(clear_button)

    layout['buttons'] = buttons

    return layout


def getMainOrderLayout(chat_id):
    order = loadOrder(chat_id)['items']
    l = {}
    if (len(order) == 0) :
        l = emptyOrderLayout()
    else:
        l = orderLayout(order)

    cb = makeCBWithID('category', None)
    b_back = makeButton(u"Добавить товар", cb)

    l['buttons'].append(b_back)

    return l



def getEditLayout(chat_id):
    order = loadOrder(chat_id)['items']

    for id in order.keys():
        if order[id].count == 0:
            order.pop(id)

    updateOrderItems(chat_id, order)

    layout = {}
    buttons = []

    for id in order:
        item = order[id]
        cb = makeItemCB(item.id)
        b = makeButton(unicode(str(item)), cb)
        buttons.append(b)

    layout['buttons'] = buttons

    return layout

def getItemLayout(chat_id, item_id):
    order = loadOrder(chat_id)['items']

    item = order[item_id]

    layout = {}
    buttons = []

    cb_plus = makeCountOrderCB(1, item_id)
    b_plus = makeButton('+1', cb_plus)
    buttons.append(b_plus)

    cb_minus = makeCountOrderCB(-1, item_id)
    b_minus = makeButton('-1', cb_minus)
    buttons.append(b_minus)

    cb_remove = makeRemoveCB(item_id)
    b_remove = makeButton(u'Удалить', cb_remove)
    buttons.append(b_remove)

    cb_ok = makeEditCB()
    b_ok = makeButton(u'Готово', cb_ok)
    buttons.append(b_ok)

    layout['buttons'] = buttons
    layout['text'] = unicode(str(item))

    return layout

def changeItemCount(chat_id, callback):
    order = loadOrder(chat_id)['items']
    item = order[callback['item_id']]

    newc = max(item.count + callback['val'], 0)
    item.count = newc

    updateItem(item, chat_id)

def removeItemById(chat_id, item_id):
    order = loadOrder(chat_id)['items']
    item = order[item_id]

    removeItem(item, chat_id)

def getOrderMenuLayout(chat_id, callback=None):
    if callback is None:
        callback = {'type': 'main'}

    layout = {}

    if callback['type'] == 'main':
        layout = getMainOrderLayout(chat_id)

    elif callback['type'] == 'clear':
        clearOrder(chat_id)
        layout = getMainOrderLayout(chat_id)

    elif callback['type'] == 'edit':
        layout = getEditLayout(chat_id)

    elif callback['type'] == 'item':
        layout = getItemLayout(chat_id, callback['id'])

    elif callback['type'] == 'count':
        changeItemCount(chat_id, callback)
        layout = getItemLayout(chat_id, callback['item_id'])

    elif callback['type'] == 'remove':
        removeItemById(chat_id, callback['item_id'])
        layout = getEditLayout(chat_id)

    return layoutComplement(layout)


#
# namespace = 'slaviktest'
# chat_id = 1
#
# bs1 = getOrderMenuLayout(chat_id)['buttons']
# bs2 = getOrderMenuLayout(chat_id, bs1[1]['callback'])['buttons']
# bs3 = getOrderMenuLayout(chat_id, bs2[0]['callback'])['buttons']
# # bs4 = getOrderMenuLayout(chat_id, bs3[3]['callback'])['buttons']
#
#
# pprint(getOrderMenuLayout(chat_id, bs3[2]['callback']))
