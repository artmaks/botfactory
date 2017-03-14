# -*- coding: utf-8 -*-
from models.Models import *
from API.register import apiRegister


def authStatus(chat_id):
    bots = [p.to_dict() for p in Users.query(Users.chat_id == str(chat_id)).fetch()]
    return len(bots) != 0


def checkAuth(func):
    def f(bot, update):
        if update.callback_query:
            chat_id = update.callback_query.message.chat_id
        else:
            chat_id = update.message.chat_id
        if not authStatus(chat_id):
            bot.sendMessage(chat_id, text='Вы не зарегистрированы в системе, пожалуйста представьтесь: ')
            return
        else:
            func(bot, update)
            return
    return f


def registerNewUser(namespace, name, chat_id):
    api_user_id = apiRegister(namespace)

    if api_user_id != 0:
        user = Users(name = name, chat_id = str(chat_id), api_user_id = str(api_user_id))
        user.put()

    return api_user_id
