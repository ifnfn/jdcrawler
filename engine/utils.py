#! /usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import logging

import tornado.escape

def autostr(i):
    if i == None:
        return ''
    if type(i) == int:
        return str(i)
    else:
        return i

def autoint(i):
    if i == None:
        return 0

    if type(i) == str:
        return i and int(i) or 0
    else:
        return i

def autofloat(i):
    if i == None:
        return 0.0

    if type(i) == str:
        return i and float(i) or 0.0
    else:
        return i;

def json_get(sets, key, default):
    if key in sets:
        return sets[key]
    else:
        return default

base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]
def dec2hex(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 16)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])

logging.basicConfig()
log = logging.getLogger("crawler")
