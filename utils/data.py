# -*- coding: utf-8 -*-
from models.Models import *

# Получить данные по имени бота (имя - ссылка в телеграмме)


def getBotDataByName(name):
    bots = [p.to_dict() for p in BotModel.query(BotModel.link == name).fetch()]
    return bots[0]