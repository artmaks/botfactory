# -*- coding: utf-8 -*-
from pprint import pprint
from API.main import makeButton, layoutComplement
# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')
# ======================= STUBS FOR LOGIC TESTING ==========================

# Stub class to be replaced by model in Models.py
class Item:
    def __init__(self, id=0, name=u"Маффин", count=1, price=120):
        self.id = id
        self.name = name
        self.count = count
        self.price = price

    def __str__(self):
        return unicode(u"{0} (x{1}) - {2}руб.".format(self.name, self.count, self.count * self.price))



order = {0: Item(0, u'Американо', 1, 120),
            1: Item(1, u'Маффин', 2, 100)}

def loadOrder(chat_id):
    # TODO: implement loading of all items in order (Platon)
    return  order

def saveOrder(chat_id, orded_state):
    global order
    order = order_state

def clearOrder(chat_id):
    # TODO: implement emptying order (Platon)
    order = {}
    saveOrder(chat_id, order)

def updateItem(item, chat_id):
    # TODO: implement updating item in order order (Platon)
    order = loadOrder(chat_id)
    order[item.id] = item
    saveOrder(chat_id, order)

def removeItem(item, chat_id):
    # TODO: implement removing item from order (Platon)
    order = loadOrder(chat_id)
    order.pop(item.id)
    saveOrder(chat_id, order)


# ========================= (supposed to be) PRODUCTION CODE ======================

# callback['type'] = 'main' | 'proc'(proceed) | 'clear' | 'edit' | 'item' | 'count' | 'remove'

def makeMainCB():
    cb = {}
    cb['type'] = 'main'
    return cb

def makeProcCB():
    cb = {}
    cb['type'] = 'proc'
    return cb

def makeClearCB():
    cb = {}
    cb['type'] = 'clear'
    return cb


def makeEditCB():
    cb = {}
    cb['type'] = 'edit'
    return cb


def makeItemCB(item_id):
    cb = {}
    cb['type'] = 'item'
    cb['id'] = item_id
    return cb


def makeCountCB(val, item_id):
    cb = {}
    cb['type'] = 'count'
    cb['val'] = val
    cb['item_id'] = item_id
    return cb


def makeRemoveCB(item_id):
    cb = {}
    cb['type'] = 'remove'
    cb['item_id'] = item_id
    return cb

def emptyOrderLayout():
    layout = {}

    layout['buttons'] = []
    layout['text'] = u"Ваш заказ пуст. Добавьте в него что-нибудь с помощью команды /menu! :)"

    return layout

def buildOrderString(order):
    lines = []

    lines.append(u'Ваш заказ:')

    for id in order:
        lines.append(str(order[id]))

    lines.append(u"\tВсего: {0}руб.".format(getOrderCost(order)))

    return '\n'.join(lines)

def orderLayout(order):
    layout = {}
    layout['text'] = buildOrderString(order)

    buttons = []

    proceed_cb = {'type': 'proc'}
    proceed_button = makeButton(u"Подтвердить", proceed_cb)
    buttons.append(proceed_button)

    edit_cb = {'type': 'edit'}
    edit_button = makeButton(u"Изменить заказ", edit_cb)
    buttons.append(edit_button)

    clear_cb = {'type': 'clear'}
    clear_button = makeButton(u"Очистить заказ", clear_cb)
    buttons.append(clear_button)

    layout['buttons'] = buttons

    return layout

def getOrderCost(order):
    cost = 0
    for id in order:
        item = order[id]
        cost += item.price * item.count
    return cost

def getMainOrderLayout(chat_id):
    order = loadOrder(chat_id)

    if (len(order) == 0) :
        return emptyOrderLayout()
    else:
        return orderLayout(order)

def getEditLayout(chat_id):
    order = loadOrder(chat_id)

    for id in order.keys():
        if order[id].count == 0:
            order.pop(id)

    saveOrderState(chat_id, order)

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
    order = loadOrder(chat_id)

    item = order[item_id]

    layout = {}
    buttons = []

    cb_plus = makeCountCB(1, item_id)
    b_plus = makeButton('+1', cb_plus)
    buttons.append(b_plus)

    cb_minus = makeCountCB(-1, item_id)
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
    order = loadOrder(chat_id)
    item = order[callback['item_id']]

    newc = max(item.count + callback['val'], 0)
    item.count = newc

    updateItem(item, chat_id)

def removeItemById(chat_id, item_id):
    order = loadOrder(chat_id)
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

    elif callback['type'] == 'proc':
        pass # TODO

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
