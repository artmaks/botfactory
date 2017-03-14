# -*- coding: utf-8 -*-
from handlers.base import BaseHandler
from handlers.message_handler import bot
from models.Models import *


class IndexHandler(BaseHandler):
    def get(self):
        bots = [p.to_dict() for p in Bot.query().fetch()]
        for i in bots:
            i['status'] = 'on' if i['token'] in bot.keys() else 'off'
        self.render('index.html', {'bots': bots})


class AddBotHandler(BaseHandler):
    def post(self):
        name = str(self.request.POST.get("botname"))
        token = str(self.request.POST.get("bottoken"))
        botlink = str(self.request.POST.get("botlink"))
        api_namespace = str(self.request.POST.get("api_namespace"))

        p = Bot(name=name, token=token, link=botlink, api_namespace=api_namespace)
        p.put()
        self.response.write('1')


class DeleteBotHandler(BaseHandler):
    def post(self):
        token = str(self.request.POST.get("bottoken"))

        if token in bot.keys():
            self.response.write("You should switch off bot before delete")
            return

        for l in Bot.query(Bot.token == token).fetch():
            l.key.delete()

        self.response.write('1')