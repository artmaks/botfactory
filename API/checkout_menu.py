# -*- coding: utf-8 -*-

from api_utils import loadOrder, saveOrder, clearOrder, makeMoveCallback, \
    makeButton, makeMainCB, buildItemsStringDict, layoutComplement, \
    TYPE

import requests
import json
from utils.data import getUserByChatId
from main import get_venues_slot, get_venues
from order_generation import convert

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def getAddresses(namespace):
    return get_venues(namespace)


def getAddressById(namespace, id):
    addrs = getAddresses(namespace)
    return addrs[list(map(lambda item: item['id'], addrs)).index(id)]['title']


def getAddressLayout(namespace):
    addrs = getAddresses(namespace)

    layout = {}
    layout['text'] = u"Где вы планируете забрать заказ?"

    buttons = []
    keys = list(map(lambda item: item['id'], addrs))

    for addr in addrs:
        cb = makeMoveCallback('place', update='address', upd_val=keys.index(addr['id']))
        button = makeButton(addr['title'], cb)
        buttons.append(button)

    cb_back = makeMainCB()
    b_back = makeButton(u'<- Назад', cb_back)
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
    b_back = makeButton(u'<- Назад', cb_back)

    buttons = [b_stay, b_out, b_back]

    layout['buttons'] = buttons

    return layout


def buildTimeString(time):
    if time == 0:
        return u'Прямо сейчас'
    else:
        return u'Через {0} минут'.format(time)


def getTimeLayout(namespace, chat_id):
    layout = {}
    layout['text'] = u"Когда планируете забрать заказ?"
    buttons = []

    address_id = loadOrder(chat_id)['address']
    time_slots = get_venues_slot(namespace, address_id)

    slot_ids = list(map(lambda item: item['id'], time_slots))

    for slot in time_slots:
        cb = makeMoveCallback('pay', update='time', upd_val=slot_ids.index(slot['id']))
        b = makeButton(slot['name'], cb)
        buttons.append(b)

    cb_back = makeMoveCallback('place')
    b_back = makeButton(u'<- Назад', cb_back)
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
    b_back = makeButton(u'<- Назад', cb_back)

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


def buildOrderString(order, namespace):
    lines = []

    itemsString = buildItemsStringDict(order['items'])
    lines.append(itemsString)

    addrString = u'Адрес: {0}'.format(getAddressById(namespace, order['address']))
    lines.append(addrString)

    placeString = getPlaceString(order['place'])
    lines.append(placeString)

    timeString = buildTimeString(order['time'])
    lines.append(timeString)

    payString = getPayString(order['pay'])
    lines.append(payString)

    return '\n'.join(lines)


def getFinalLayout(order, namespace):
    layout = {}
    layout['text'] = buildOrderString(order, namespace)
    buttons = []

    cb_submit = makeMoveCallback('submit')
    b_submit = makeButton(u'Подтвердить', cb_submit)
    buttons.append(b_submit)

    cb_back = makeMoveCallback('pay')
    b_back = makeButton(u'<- Назад', cb_back)
    buttons.append(b_back)

    layout['buttons'] = buttons

    return layout


def submitOrder(namespace, chat_id):
    order_json = convert(namespace, chat_id)
    return requests.post('http://%s.1.doubleb-automation-production.appspot.com/api/order' % namespace,
                  params={'order': json.dumps(order_json)}), order_json


def transformUpdToId(namespace, chat_id, field_name, upd):
    addrs = getAddresses(namespace)
    if field_name == 'address':
        curr_addr_id = addrs[upd]['id']
        return curr_addr_id
    if field_name == 'time':
        order = loadOrder(chat_id)
        slots = get_venues_slot(namespace, order['address'])
        return slots[upd]['id']
    return upd


def getCheckoutMenuLayout(namespace, chat_id, callback):
    order = loadOrder(chat_id)

    if 'update' in callback and callback['update'] is not None:
        order[callback['update']] = transformUpdToId(namespace, chat_id, callback['update'], callback['val'])
        saveOrder(chat_id, order)

    if callback[TYPE] == 'address':
        layout = getAddressLayout(namespace)

    elif callback[TYPE] == 'place':
        layout = getPlaceLayout()

    elif callback[TYPE] == 'time':
        layout = getTimeLayout(namespace, chat_id)

    elif callback[TYPE] == 'pay':
        layout = getPayLayout()

    elif callback[TYPE] == 'final':
        layout = getFinalLayout(order, namespace)

    elif callback[TYPE] == 'submit':
        res, order_json = submitOrder(namespace, chat_id)
        # check success
        clearOrder(chat_id)
        layout = {'text': u'Заказ успешно добавлен %s!' % res.text}

    layout = layoutComplement(layout)
    return layout


def getOrderSubmissionJSON(usr, order):
    return {
        "client": {
            "email": "",
            "id": str(usr['api_user_id']),
            "name": str(usr['name']),
            "phone": ""
        },
        "comment": "",
        "coordinates": "0.0,0.0",
        "delivery_sum": 0,
        "device_type": 1,
        "order_gifts": [
        ],
        "payment": {
            "binding_id": None,
            "client_id": None,
            "return_url": None,
            "type_id": 0,
            "wallet_payment": 0
        },
        "total_sum": 250,
        "venue_id": "5720147234914304",
        "items": [
            {
                "quantity": 1,
                "item_id": "5692462144159744",
                "single_modifiers": [
                ],
                "group_modifiers": [
                    {
                        "group_modifier_id": "5652383656837120",
                        "choice": "10",
                        "quantity": 1
                    }
                ]
            },
            {
                "quantity": 1,
                "item_id": "5091364022779904",
                "single_modifiers": [
                ],
                "group_modifiers": [
                    {
                        "group_modifier_id": "5652383656837120",
                        "choice": "183",
                        "quantity": 1
                    }
                ]
            }
        ],
        "gifts": [
        ],
        "after_error": False,
        "delivery_type": 0,
        "delivery_slot_id": "5639445604728832",
        "time_picker_value": "2017-03-25 15:20:10"
    }
