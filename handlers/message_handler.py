#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.path.abspath('.'), 'venv/Lib/site-packages'))

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from credentials import TOKEN
from handlers.bot_handlers import order, error, help, start, namespace, menu, menu_button, text_handler

dispatcher = {}
bot = {}


def setup(token):
    '''GAE DISPATCHER SETUP'''
    bot[token] = Bot(token)

    global dispatcher
    # Note that update_queue is setted to None and
    # 0 workers are allowed on Google app Engine (If not-->Problems with multithreading)
    dispatcher[token] = Dispatcher(bot=bot[token], update_queue=None, workers=0)

    # ---Register handlers here---
    dispatcher[token].add_handler(CommandHandler("start", start))
    dispatcher[token].add_handler(CommandHandler("help", help))
    dispatcher[token].add_handler(CommandHandler("order", order))
    dispatcher[token].add_handler(CommandHandler("namespace", namespace))
    dispatcher[token].add_handler(CommandHandler("menu", menu))
    dispatcher[token].add_handler(MessageHandler(Filters.text, text_handler))
    dispatcher[token].add_handler(CallbackQueryHandler(menu_button))
    dispatcher[token].add_error_handler(error)

    return dispatcher[token]


def webhook(update, token):
    global dispatcher
    # Manually get updates and pass to dispatcher
    dispatcher[token].process_update(update)