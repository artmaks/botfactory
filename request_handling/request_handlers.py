# -*- coding: utf-8 -*-
#!/usr/bin/env python

from webapp2 import RequestHandler

from credentials import APP_URL
from request_handling.base import BaseHandler
from request_handling.bot_registry import bots, dispatchers
from request_handling.bot_registry import setup_bot
from models.Models import *
import json
import telegram
from webapp2 import RequestHandler
from request_handling.bot_registry import bots, process_webhook_call


class WebHookOperationsHandler(RequestHandler):
    def set_webhook(self, token):
        '''
        Set webhook for your bot
        '''
        if token in bots:
            self.response.write("0")
            return

        setup_bot(token)
        url = APP_URL + '/bot_handler/' + token
        s = bots[token].setWebhook(url)
        if s:
            self.response.write("1")
        else:
            self.response.write("-1")

    def unset_webhook(self, token):
        if token not in bots:
            self.response.write("0")
        else:
            s = bots[token].setWebhook("")
            if s:
                del bots[token]
                del dispatchers[token]
                self.response.write("1")
            else:
                self.response.write("-1")


class IndexHandler(BaseHandler):
    def get(self):
        bots_data = [p.to_dict() for p in BotModel.query().fetch()]
        for i in bots_data:
            i['status'] = 'on' if i['token'] in bots.keys() else 'off'
        self.render('index.html', {'bots': bots_data})


class AddBotHandler(BaseHandler):
    def post(self):
        name = str(self.request.POST.get("botname"))
        token = str(self.request.POST.get("bottoken"))
        botlink = str(self.request.POST.get("botlink"))
        api_namespace = str(self.request.POST.get("api_namespace"))

        p = BotModel(name=name, token=token, link=botlink, api_namespace=api_namespace)
        p.put()
        self.response.write('1')


class DeleteBotHandler(BaseHandler):
    def post(self):
        token = str(self.request.POST.get("bottoken"))

        if token in bots.keys():
            self.response.write("You should switch off bot before delete")
            return

        for l in BotModel.query(BotModel.token == token).fetch():
            l.key.delete()

        self.response.write('1')


class WebHookHandler(RequestHandler):
    def webhook_handler(self, token):
        # Retrieve the message in JSON and then transform it to Telegram object
        body = json.loads(self.request.body)
        update = telegram.Update.de_json(body, bots[token])
        process_webhook_call(update, token)