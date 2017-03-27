# -*- coding: utf-8 -*-
import requests
import json
# from google.appengine.ext import ndb
from pprint import pprint
# from utils.data import Item
from API.api_utils import loadOrder, getOrderCost
from time import gmtime, strftime
from API.main import get_menu
from utils.data import getUserByChatId
# from API.order_menu import makeMainCB

import sys
reload(sys)
sys.setdefaultencoding('utf8')


BASE_JSON = json.loads('{"client":{},"comment":"","coordinates":"0.0,0.0","delivery_sum":0,"device_type":1,"order_gifts":[],"payment":{"binding_id":null,"client_id":null,"return_url":null,"type_id":0,"wallet_payment":0},"total_sum":250,"venue_id":"5720147234914304","items":[{"quantity":1,"item_id":"5692462144159744","single_modifiers":[],"group_modifiers":[{"group_modifier_id":"5652383656837120","choice":"10","quantity":1}]},{"quantity":1,"item_id":"5091364022779904","single_modifiers":[],"group_modifiers":[{"group_modifier_id":"5652383656837120","choice":"183","quantity":1}]}],"gifts":[],"after_error":false,"delivery_type":0,"delivery_slot_id":"5639445604728832","time_picker_value":"2017-03-25 15:20:10"}')

pprint(BASE_JSON)

def getItemByIdRec(id, categories):
    for cat in categories:
        if len(cat['categories']) > 0:
            res = getItemByIdRec(id, cat['categories'])
            if res is not None:
                return res

        else:
            for item in cat['items']:
                if item['id'] == id:
                    return item

        return None


def getGroupModifiers(namespace, ids):
    menu = get_menu(namespace)['menu']

    gmods_conv = []

    item_id = ids[0]
    mod_ids = ids[1:]

    item = getItemByIdRec(item_id, menu)

    if item is None:
        return gmods_conv

    gmods = item['group_modifiers']

    for (gmod, id) in zip(gmods, mod_ids):
        gmod_conv = {}
        gmod_conv['group_modifier_id'] = gmod['modifier_id']
        gmod_conv['quantity'] = 1
        gmod_conv['choice'] = id

        gmods_conv.append(gmod_conv)

    return gmods_conv



def convertItems(namespace, items):
    items_conv = []

    for id in items:
        item = items[id]
        item_conv = {}

        ids = item.getId().split('#')

        item_conv['quantity'] = item.getCount()
        item_conv['item_id'] = ids[0]
        item_conv['single_modifiers'] = {}
        item_conv['group_modifiers'] = getGroupModifiers(namespace, ids)

        items_conv.append(item_conv)

    return items_conv


def convert(namespace, chat_id):
    res = BASE_JSON

    user = getUserByChatId(chat_id)

    res['client']['name'] = user['name']
    res['client']['id'] = user['api_user_id']
    res['client']['phone'] = "89996793459"

    order = loadOrder(chat_id)

    res['venue_id'] = order['address']
    res['delivery_slot_id'] = order['time']

    res['total_sum'] = getOrderCost(order['items']) # change to getOrderCostDict if it doesn't work

    res['time_picker_value'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    res['items'] = convertItems(namespace, order['items'])

    return res