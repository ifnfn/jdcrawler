#!env python3
# -*- coding: utf-8 -*-

import engine
import pymongo
import threading

class Crawler:
    def __init__(self, thread_num=1):
        self.threads = []
        for _ in range(thread_num):
            self.threads.append(Work(self))

        self.tv = engine.KolaEngine()
        self.tv.Start()
        self.db = pymongo.MongoClient().sumfeel
        self.db_goods = self.db.goods

    def Wait(self):
        for item in self.threads:
            item.start()
        for item in self.threads:
            if item.isAlive():item.join()

    def RunOne(self):
        cmd = self.tv.GetCommand()
        if cmd:
            data = self.tv.ProcessCommand(cmd, 3)
            if data:
                self.db_goods.insert_one(data)
                return True
        return False

class Work(threading.Thread):
    def __init__(self, crawler):
        super().__init__()
        self.crawler = crawler

    def run(self):
        while True:
            self.crawler.RunOne()

def main():
    Crawler(4).Wait()

if __name__ == '__main__':
   main()
