#!env python3
# -*- coding: utf-8 -*-

import engine
from kola.ThreadPool import ThreadPool

tv = engine.KolaEngine()

def main():
    tv.Start()

    while True:
        cmd = tv.GetCommand()
        if cmd:
            data = tv.ProcessCommand(cmd, 3)
            print(data)
        else:
            break

def main_thread():
    thread_pool = ThreadPool(2)
    for _ in range(100):
        thread_pool.add_job(main)

if __name__ == '__main__':
    # main_thread()
   main()
