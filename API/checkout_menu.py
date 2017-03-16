# -*- coding: utf-8 -*-

from api_utils import loadOrder, saveOrder, makeMoveCallback, \
    makeButton, makeMainCB, buildItemsString, layoutComplement

import sys
reload(sys)
sys.setdefaultencoding('utf8')


addrs = {0: u'ул. Маршала Бирюзова 5', 1: u'пр. Мира 57'}

def getAddresses(namespace):
    return addrs

def getAddressById(namespace, id):
    addrs = getAddresses(namespace)
    return addrs[id]

def getAddressLayout(namespace):
    addrs  = getAddresses(namespace)

    layout = {}
    layout['text'] = u"Где вы планируете забрать заказ?"

    buttons = []

    for id in addrs:
        cb = makeMoveCallback('place', update='address', upd_val=id)
        button = makeButton(addrs[id], cb)
        buttons.append(button)

    cb_back = makeMainCB()
    b_back = makeButton(u'Назад', cb_back)
    buttons.append(b_back)

    layout['buttons'] = buttons

    return layout


def getPlaceLayout():
    layout = {}

    layout['text'] = u"Где вы планируете есть?"

    cb_stay = makeMoveCallback('time', 'place', 'stay')
    b_stay = makeButton(u'В кафе', cb_stay)

    cb_out = makeMoveCallback('time', 'place', 'out')
    b_out = makeButton(u'С собой', cb_out)

    cb_back = makeMoveCallback('address')
    b_back = makeButton(u'Назад', cb_back)

    buttons = [b_stay, b_out, b_back]

    layout['buttons'] = buttons

    return layout

def buildTimeString(time):
    if time == 0:
        return u'Прямо сейчас'
    else:
        return u'Через {0} минут'.format(time)

def getTimeLayout():
    layout = {}

    layout['text'] = u"Когда планируете забрать заказ?"

    buttons = []

    for i in range(4):
        aft = i*5
        cb = makeMoveCallback('pay', 'time', aft)
        b = makeButton(buildTimeString(aft), cb)
        buttons.append(b)

    cb_back = makeMoveCallback('place')
    b_back = makeButton(u'Назад', cb_back)
    buttons.append(b_back)

    layout['buttons'] = buttons

    return layout


def getPayLayout():
    layout = {}

    layout['text'] = u"Оплата:"

    cb_cash = makeMoveCallback('final', 'pay', 'cash')
    b_cash = makeButton(u'Наличными', cb_cash)

    cb_card = makeMoveCallback('final', 'pay', 'card')
    b_card = makeButton(u'Картой', cb_card)

    cb_back = makeMoveCallback('time')
    b_back = makeButton(u'Назад', cb_back)

    buttons = [b_cash, b_card, b_back]

    layout['buttons'] = buttons

    return layout

def getPlaceString(place):
    if place == 'stay':
        return u'В кафе'
    elif place == 'out':
        return u'С собой'

def getPayString(pay):
    if pay == 'cash':
        return u'Оплата наличными'
    elif pay == 'card':
        return u'Оплата картой'


def buildOrderString(order):
    lines = []

    itemsString = buildItemsString(order['items'])
    lines.append(itemsString)

    addrString = u'Адрес: {0}'.format(getAddressById(order['address']))
    lines.append(addrString)

    placeString = getPlaceString(order['place'])
    lines.append(placeString)

    timeString = buildTimeString(order['time'])
    lines.append(timeString)

    payString = getPayString(order['pay'])
    lines.append(payString)

    return '\n'.join(lines)

def getFinalLayout(order):
    layout = {}
    layout['text'] = buildOrderString(order)
    buttons = []

    cb_submit = makeMoveCallback('submit')
    b_submit = makeButton(u'Подтвердить', cb_submit)
    buttons.append(b_submit)

    cb_back = makeMoveCallback('pay')
    b_back = makeButton(u'Назад', cb_back)
    buttons.append(b_back)

    layout['buttons'] = buttons

    return layout


def submitOrder(namespace, chat_id, order):
    pass

def getCheckoutMenuLayout(namespace, chat_id, callback):

    order = loadOrder(chat_id)

    if 'update' in callback and callback['update'] is not None:
        order[callback['update']] = callback['val']
        saveOrder(chat_id, order)

    if callback['type'] == 'address':
        layout = getAddressLayout(namespace)

    elif callback['type'] == 'place':
        layout = getPlaceLayout()

    elif callback['type'] == 'time':
       layout = getTimeLayout()

    elif callback['type'] == 'pay':
        layout = getPayLayout()

    elif callback['type'] == 'final':
        layout = getFinalLayout(order)

    elif callback['type'] == 'submit':
        submitOrder(namespace, chat_id, order)
        layout = {'text': u'Заказ успешно добавлен!'}

    layout = layoutComplement(layout)
    return layout

