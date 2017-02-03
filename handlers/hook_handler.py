#!/usr/bin/env python
from webapp2 import RequestHandler

import telegram
from telegram import bot
from message_handler import bot, setup, webhook, dispatcher
from credentials import TOKEN, APP_URL
import json

class WebHookHandler(RequestHandler):
    def set_webhook(self, token):
        '''
        Set webhook for your bot
        '''
        setup(token)
        url = APP_URL + '/bot_handler/' + token;
        s = bot[token].setWebhook(url)
        if s:
            self.response.write("1")
        else:
            self.response.write("0")

    def unset_webhook(self, token):
        if(token not in bot.keys()):
            self.response.write("0")
        else:
            s = bot[token].setWebhook("")
            if s:
                del bot[token]
                del dispatcher[token]
                self.response.write("1")
            else:
                self.response.write("-1")

    def webhook_handler(self, token):
        # Retrieve the message in JSON and then transform it to Telegram object
        body = json.loads(self.request.body)
        update = telegram.Update.de_json(body, bot[token])
        webhook(update, token)