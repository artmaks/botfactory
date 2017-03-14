# -*- coding: utf-8 -*-
import requests
import json

def apiRegister(namespace):
    url = 'http://%s.1.doubleb-automation-production.appspot.com/api/register' % (namespace)
    res = requests.post(url)
    if (res.ok):
        return json.loads(res.content)['client_id']
    else:
        return 0