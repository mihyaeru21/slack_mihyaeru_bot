# -*- coding: utf-8 -*-

import time

from slacker import Slacker
from slackclient import SlackClient

import config

class SlackBot(object):
    def __init__(self):
        self.config = config
        self.api    = Slacker(self.config.token)
        self.client = SlackClient(self.config.token)

    def run(self):
        self.client.rtm_connect()
        while True:
            for data in self.client.rtm_read():
                print data
            time.sleep(1)

def main():
    print 'run'
    bot = SlackBot()
    bot.run()

if __name__ == '__main__':
    main()

