# -*- coding: utf-8 -*-
from google.appengine.ext import ndb, db


class BotModel(ndb.Model):
    name = ndb.StringProperty(default='')
    token = ndb.StringProperty(default='')
    link = ndb.StringProperty(default='')
    api_namespace = ndb.StringProperty(default='')


class Users(ndb.Model):
    name = ndb.StringProperty(default='')
    chat_id = ndb.StringProperty(default='')
    api_user_id = ndb.StringProperty(default='')


class Order(ndb.Model):
    name = ndb.StringProperty(default='')
    chat_id = ndb.StringProperty(default='')
    active = ndb.BooleanProperty(default=True)


class OrderItem(ndb.Model):
    name = ndb.StringProperty(default='')
    content = ndb.StringProperty(default='')
    count = ndb.IntegerProperty()


class Category(ndb.Model):
    name = ndb.StringProperty(default='')
    description = ndb.StringProperty(default='')


class NavigationState(ndb.Model):
    path = ndb.StringProperty(default='')

#
# class Product(ndb.Model):
#     name = ndb.StringProperty(default='')
#     description = ndb.StringProperty(default='')
#     available = ndb.BooleanProperty(default=True)
