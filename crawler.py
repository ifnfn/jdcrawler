#!env python3
# -*- coding: utf-8 -*-

import os
from urllib.parse import unquote
import zlib, sys

import engine
import kola


def main():
    tv = engine.KolaEngine()
    tv.Start()

    while True:
        cmd = tv.command.GetCommand() # 拿到一条解析命令
        if cmd:
            tv.ProcessCommand(cmd, 3)
        else:
            break


if __name__ == '__main__':
    main()
