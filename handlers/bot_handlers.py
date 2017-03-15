# -*- coding: utf-8 -*-
from handlers.message_handler import logger
from API.main import *
from models.Models import *
from API.main import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.register import authStatus, checkAuth, registerNewUser
from utils.data import *
import json
from google.appengine.ext import ndb

orders = {}


def text_handler(bot, update):
    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)
    namespace = data['api_namespace']
    name = update.message.text
    chat_id = update.message.chat_id

    if not authStatus(update.message.chat_id):
        bot.sendMessage(chat_id=chat_id, text=u"Добрый день, " + name + u"!")
        user_id = registerNewUser(namespace, name, chat_id)
        if user_id != 0:
            bot.sendMessage(chat_id=chat_id, text=u"Вы успешно были зарегистрированы в системе, ваш user_id " + str(user_id))
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Для просмотра списка комманд введите /help")


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


#Получить namespace для API бота (в будущем эта функция не нужна)
def namespace(bot, update):
    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)

    bot.sendMessage(update.message.chat_id, text=data['api_namespace'])


#Получить меню
@checkAuth
def menu(bot, update):
    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)
    new_order = Order(chat_id=str(update.message.chat_id))
    new_order.put()

    # categories = getCategories(data['api_namespace'])
    layout = getMenuLayout(data['api_namespace'], update.message.chat_id)

    keyboard = []
    for i in layout['buttons']:
        name = i['name']
        callback = json.dumps(i['callback'])
        keyboard.append([InlineKeyboardButton(name, callback_data=callback)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Menu:', reply_markup=reply_markup)


@checkAuth
def menu_button(bot, update):
    query = update.callback_query

    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)

    # items = getItems(data['api_namespace'], query.data)
    layout = getMenuLayout(data['api_namespace'], query.message.chat_id, json.loads(query.data))

    keyboard = []
    for i in layout['buttons']:
        name = i['name']
        callback = json.dumps(i['callback'])
        keyboard.append([InlineKeyboardButton(name, callback_data=callback)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.editMessageText(text="Menu: \n" + (layout['text'] or ''),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)


@checkAuth
def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


@checkAuth
def order(bot, update):
    chat_id = update.message.chat_id
    if chat_id in orders:
        bot.sendMessage(chat_id, text='You are already ordering!')
    else:
        new_order = Order(key_name=chat_id)
        new_order.put()
        bot.sendMessage(chat_id, text='New order started!')


@checkAuth
def finalize_order(bot, update):
    chat_id = update.message.chat_id
    if chat_id in orders:
        del orders[chat_id]
        bot.sendMessage(chat_id, text='Proceeding to checkout!')
        order = getOrderByChatId(chat_id)
        order.put()
    else:
        bot.sendMessage(chat_id, text='No active order!')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
