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
from request_handling.bot_command_handlers import *

dispatchers = {}
bots = {}


def setup_bot(token):
    '''GAE DISPATCHER SETUP'''
    bots[token] = Bot(token)

    global dispatchers
    # Note that update_queue is setted to None and
    # 0 workers are allowed on Google app Engine (If not-->Problems with multithreading)
    dispatchers[token] = Dispatcher(bot=bots[token], update_queue=None, workers=0)

    # ---Register request_handling here---
    dispatchers[token].add_handler(CommandHandler("start", start))
    dispatchers[token].add_handler(CommandHandler("help", help))
    dispatchers[token].add_handler(CommandHandler("namespace", namespace))
    dispatchers[token].add_handler(CommandHandler("menu", menu))
    dispatchers[token].add_handler(MessageHandler(Filters.text, text_handler))
    dispatchers[token].add_handler(CallbackQueryHandler(menu_button))
    dispatchers[token].add_error_handler(error)

    return dispatchers[token]


def process_webhook_call(update, token):
    global dispatchers
    # Manually get updates and pass to dispatcher
    dispatchers[token].process_update(update)
