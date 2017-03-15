# -*- coding: utf-8 -*-

def makeButton(name, callback):
    return {'name': name, 'callback': callback}

def layoutComplement(layout):
    if 'buttons' not in layout:
        layout['buttons'] = []

    if 'img' not in layout:
        layout['img'] = None

    if 'text' not in layout:
        layout['text'] = None

    return layout
