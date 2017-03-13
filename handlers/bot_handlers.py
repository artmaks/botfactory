# -*- coding: utf-8 -*-
from handlers.message_handler import logger
from models.Models import *

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