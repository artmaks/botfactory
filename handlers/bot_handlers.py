# -*- coding: utf-8 -*-
from handlers.message_handler import logger
from API.main import *
from models.Models import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.register import authStatus, checkAuth, registerNewUser
from utils.data import getBotDataByName
from google.appengine.ext import ndb, db

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
    categories = get_categories(data['api_namespace'])

    keyboard = []
    for i in categories:
        keyboard.append([InlineKeyboardButton(i, callback_data=i)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Menu:', reply_markup=reply_markup)


@checkAuth
def menu_button(bot, update):
    query = update.callback_query
    chat_id = update.message.chat_id

    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)
    if data['type'] == 'category':
        items = get_items(data['api_namespace'], query.data)

        keyboard = []
        for i in items:
            keyboard.append([InlineKeyboardButton(i, callback_data=i)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.editMessageText(text="Menu:",
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            reply_markup=reply_markup)
    elif data['type'] == 'item':
        pass
    elif data['type'] == 'option':
        pass
    elif data['type'] == 'add':
        item = data['item']
        order = db.Key.from_path('Order', chat_id)
        new_item = OrderItem(parent=order, name='name', content=item)
        new_item.put()



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
def checkout(bot, update):
    chat_id = update.message.chat_id
    if chat_id in orders:
        del orders[chat_id]
        bot.sendMessage(chat_id, text='Proceeding to checkout!')
    else:
        bot.sendMessage(chat_id, text='No active order!')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
