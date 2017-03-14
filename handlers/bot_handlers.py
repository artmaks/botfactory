# -*- coding: utf-8 -*-
from handlers.message_handler import logger
from models.Models import *
from API.main import getMenu, getCategories, getItems
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

orders = {}

# Получить данные по имени бота (имя - ссылка в телеграмме)
def getBotDataByName(name):
    bots = [p.to_dict() for p in BotModel.query(BotModel.link == name).fetch()]
    return bots[0]

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')

#Получить namespace для API бота (в будущем эта функция не нужна)
def namespace(bot, update):
    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)

    bot.sendMessage(update.message.chat_id, text=data['api_namespace'])

#Получить меню
def menu(bot, update):
    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)
    categories = getCategories(data['api_namespace'])

    keyboard = []
    for i in categories:
        keyboard.append([InlineKeyboardButton(i, callback_data=i)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Menu:', reply_markup=reply_markup)

def menu_button(bot, update):
    query = update.callback_query

    bot_name = bot.name.replace('@', '')
    data = getBotDataByName(bot_name)
    items = getItems(data['api_namespace'], query.data)

    keyboard = []
    for i in items:
        keyboard.append([InlineKeyboardButton(i, callback_data=i)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.editMessageText(text="Menu:",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def order(bot, update):
    chat_id = update.message.chat_id
    if chat_id in orders:
        bot.sendMessage(chat_id, text='You are already ordering!')
    else:
        orders[chat_id] = "order"
        bot.sendMessage(chat_id, text='New order started!')


def checkout(bot, update):
    chat_id = update.message.chat_id
    if chat_id in orders:
        del orders[chat_id]
        bot.sendMessage(chat_id, text='Proceeding to checkout!')
    else:
        bot.sendMessage(chat_id, text='No active order!')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))