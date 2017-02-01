# -*- coding: utf-8 -*-
import webapp2
import json
from handlers.base import *


class IndexHandler(BaseHandler):
    def get(self):

        self.render('index.html', {'data_hello' : "Hello", 'data_world' : "World!"})

    def post(self):
        self.response.write('post запрос недоступен')