# -*- coding: utf-8 -*-
from handlers.message_handler import logger

orders = {}


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


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