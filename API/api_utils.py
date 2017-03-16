# -*- coding: utf-8 -*-

import json

from utils.data import getMenuStateByChatId, updateMenuStateByChatId

from utils.data import  getOrderStateByChatId, updateOrderStateByChatId
from utils.data import defaultOrder

ITEM_CHAT = 'i'
ORDER_CHAT = 'o'
CHECKOUT_CHAT = 'c'

# ============ Item callbacks ===============

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

def makeCountItemCB(val):
    cb = makeEmptyCB('count')
    cb['val'] = val
    return cb


# ============= Order callbacks =============

def makeOrderCB():
    cb = {}
    cb['chat'] = ORDER_CHAT
    return cb

def makeMainCB():
    cb = makeOrderCB()
    cb['type'] = 'main'
    return cb

def makeProcCB():
    cb = makeOrderCB()
    cb['type'] = 'proc'
    return cb

def makeClearCB():
    cb = makeOrderCB()
    cb['type'] = 'clear'
    return cb


def makeEditCB():
    cb = makeOrderCB()
    cb['type'] = 'edit'
    return cb


def makeItemCB(item_id):
    cb = makeOrderCB()
    cb['type'] = 'item'
    cb['id'] = item_id
    return cb


def makeCountOrderCB(val, item_id):
    cb = makeOrderCB()
    cb['type'] = 'count'
    cb['val'] = val
    cb['item_id'] = item_id
    return cb


def makeRemoveCB(item_id):
    cb = makeOrderCB()
    cb['type'] = 'remove'
    cb['item_id'] = item_id
    return cb


# ================ Checkout callbacks ================

def makeCheckoutCB():
    cb = {}
    cb['chat'] = CHECKOUT_CHAT
    return cb

def makeMoveCallback(to, update=None, upd_val=None):
    cb = makeCheckoutCB()
    cb['type'] = to
    cb['update'] = update
    cb['val'] = upd_val
    return cb


# ============ Loading data ================

# Menu state

def getStateByChatId(chat_id):
    return json.loads(getMenuStateByChatId(chat_id))

def saveState(chat_id, st):
    updateMenuStateByChatId(chat_id, st)

# Order state

def loadOrder(chat_id):
    return getOrderStateByChatId(chat_id)

def updateOrderItems(chat_id, items):
    order = loadOrder(chat_id)
    order['items'] = items
    saveOrder(chat_id, order)

def saveOrder(chat_id, order_state):
    updateOrderStateByChatId(chat_id, order_state)


def clearOrder(chat_id):
    order = defaultOrder()
    saveOrder(chat_id, order)

def updateItem(item, chat_id):
    order = loadOrder(chat_id)
    order['items'][item.id] = item
    saveOrder(chat_id, order)

def removeItem(item, chat_id):
    order = loadOrder(chat_id)
    order['items'].pop(item.id)
    saveOrder(chat_id, order)



# ============ Other ===================

def makeButton(name, callback):
    return {'name': name, 'callback': callback}

def layoutComplement(layout):
    if 'buttons' not in layout:
        layout['buttons'] = []

    if 'img' not in layout:
        layout['img'] = None

    if 'text' not in layout:
        layout['text'] = None

    return layout

def getOrderCost(order):
    cost = 0
    for id in order:
        item = order[id]
        cost += item.price * item.count
    return cost


def buildItemsString(order):
    lines = []

    lines.append(u'Ваш заказ:')

    for id in order:
        lines.append(str(order[id]))

    lines.append(u"\tВсего: {0}руб.".format(getOrderCost(order)))

    return '\n'.join(lines)