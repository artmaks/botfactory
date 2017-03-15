# -*- coding: utf-8 -*-
from models.Models import BotModel, NavigationState, OrderState
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# Получить данные по имени бота (имя - ссылка в телеграмме)


def getBotDataByName(name):
    bots = [p.to_dict() for p in BotModel.query(BotModel.link == name).fetch()]
    return bots[0]

def resetMenuState(chat_id, message_id):
    all_states = NavigationState.query(NavigationState.chat_id == str(chat_id)).fetch()

    for l in all_states:
        l.key.delete()

    state_entity = NavigationState(chat_id=str(chat_id), state='{"steps": []}', message_id = message_id)
    state_entity.put()

#======= Menu ======
def getCurrentMenuMessage(chat_id):
    state = [p.to_dict() for p in NavigationState.query(NavigationState.chat_id == str(chat_id)).fetch()]
    return state[0]['message_id'] if len(state) > 0 else None

def getMenuStateByChatId(chat_id):
    state = [p.to_dict() for p in NavigationState.query(NavigationState.chat_id == str(chat_id)).fetch()]
    return state[0]['state'] if len(state) > 0 else '{"steps": []}'

def updateMenuStateByChatId(chat_id, new_state):
    json_state = json.dumps(new_state)
    state = NavigationState.query(NavigationState.chat_id == str(chat_id)).fetch()
    if len(state) != 1:
        for l in state:
            l.key.delete()

        state_entity = NavigationState(chat_id = str(chat_id), state = json_state)
        state_entity.put()
    else:
        state_entity = state[0].key.get()
        state_entity.state = json_state
        state_entity.put()

#======= Orders state ======

def orderDictToOrder(order_dict):
    order = {i: Item.from_dict(order_dict[i]) for i in order_dict}
    return order

def orderToOrderDict(order):
    order_dict = {i: order[i].to_dict() for i in order}
    return order_dict

def getOrderStateByChatId(chat_id):
    state = [p.to_dict() for p in OrderState.query(OrderState.chat_id == str(chat_id)).fetch()]
    if len(state) == 0:
        return {}

    state_items = orderDictToOrder(json.loads(state[0]['state']))
    return state_items

def updateOrderStateByChatId(chat_id, new_state):
    new_state_dicts = orderToOrderDict(new_state)
    json_state = json.dumps(new_state_dicts)
    state = OrderState.query(OrderState.chat_id == str(chat_id)).fetch()
    if len(state) != 1:
        for l in state:
            l.key.delete()

        state_entity = OrderState(chat_id = str(chat_id), state = json_state)
        state_entity.put()
    else:
        state_entity = state[0].key.get()
        state_entity.state = json_state
        state_entity.put()


# ========= Order Item ==========

class Item:
    def __init__(self, id=0, name=u"Маффин", count=1, price=120):
        self.id = id
        self.name = name
        self.count = count
        self.price = price

    def __str__(self):
        return unicode(u"{0} (x{1}) - {2}руб.".format(self.name, self.count, self.count * self.price))

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(map):
        return Item(map)
