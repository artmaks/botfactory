# -*- coding: utf-8 -*-
import webapp2
import json
from handlers.base import BaseHandler
from message_handler import bot
from models.Models import *

class IndexHandler(BaseHandler):
    def get(self):
        bots = [p.to_dict() for p in BotModel.query().fetch()]
        for i in bots:
            i['status'] = 'on' if i['token'] in bot.keys() else 'off'
        self.render('index.html', {'bots' : bots})