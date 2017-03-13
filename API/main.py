# -*- coding: utf-8 -*-
import requests
import json

def getMenu(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/menu' % (namespace)
    res = requests.get(url)
    if (res.ok):
        return json.loads(res.content)
    else:
        return 'Error'