# -*- coding: utf-8 -*-
from models.Models import *
import json

# Получить данные по имени бота (имя - ссылка в телеграмме)


def getBotDataByName(name):
    bots = [p.to_dict() for p in BotModel.query(BotModel.link == name).fetch()]
    return bots[0]

def getOrderByChatId(chat_id):
    orders = [p.to_dict() for p in Order.query(Order.chat_id == str(chat_id) and Order.active == True).fetch()]
    return orders[0]

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

def getOrderStateByChatId(chat_id):
    state = [p.to_dict() for p in OrderState.query(OrderState.chat_id == str(chat_id)).fetch()]
    return state[0]['state'] if len(state) > 0 else '{}'

def updateOrderStateByChatId(chat_id, new_state):
    json_state = json.dumps(new_state)
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