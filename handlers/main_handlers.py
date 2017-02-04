# -*- coding: utf-8 -*-
from handlers.base import BaseHandler
from handlers.message_handler import bot
from models.Models import *


class IndexHandler(BaseHandler):
    def get(self):
        bots = [p.to_dict() for p in BotModel.query().fetch()]
        for i in bots:
            i['status'] = 'on' if i['token'] in bot.keys() else 'off'
        self.render('index.html', {'bots' : bots})

class AddBotHandler(BaseHandler):
    def post(self):
        name = str(self.request.POST.get("botname"))
        token = str(self.request.POST.get("bottoken"))
        botlink = str(self.request.POST.get("botlink"))

        p = BotModel(name=name, token=token, link=botlink)
        p.put()
        self.response.write('1')

class DeleteBotHandler(BaseHandler):
    def post(self):
        token = str(self.request.POST.get("bottoken"))

        if token in bot.keys():
            self.response.write("You should switch off bot before delete")
            return

        for l in BotModel.query(BotModel.token == token).fetch():
            l.key.delete()

        self.response.write('1')