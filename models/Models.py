# -*- coding: utf-8 -*-
from google.appengine.ext import ndb


class BotModel(ndb.Model):
    name = ndb.StringProperty(default='')
    token = ndb.StringProperty(default='')
    link = ndb.StringProperty(default='')
    api_namespace = ndb.StringProperty(default='')

class Users(ndb.Model):
    name = ndb.StringProperty(default='')
    chat_id = ndb.StringProperty(default='')
    api_user_id = ndb.StringProperty(default='')