# -*- coding: utf-8 -*-
from google.appengine.ext import ndb

class Bot(ndb.Model):
    name = ndb.StringProperty(default='')
    token = ndb.StringProperty(default='')
