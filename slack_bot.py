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
        self.plugins = []
        self.user_map    = {}
        self.channel_map = {}
        self.load_plugins()

    def run(self):
        self.update_maps()
        self.client.rtm_connect()
        while True:
            for event in self.client.rtm_read():
                self.combine_maps(event)
                for plugin in self.plugins:
                    plugin.process_event(event)
            time.sleep(1)

    def update_maps(self):
        for user in self.api.users.list().body['members']:
            self.user_map[user['id']] = user
        for channel in self.api.channels.list().body['channels']:
            self.channel_map[channel['id']] = channel
        for group in self.api.groups.list().body['groups']:
            self.channel_map[group['id']] = group

    def combine_maps(self, event):
        user_id = event.get('user')
        if user_id is not None:
            user = self.user_map.get(user_id)
            if user is not None:
                event['user_dict'] = user
        channel_id = event.get('channel')
        if channel_id is not None:
            channel = self.channel_map.get(channel_id)
            if channel is not None:
                event['channel_dict'] = channel

    # for override
    def plugin_classes(self):
        return [
            EventTypePlugin,
            PrintPlugin,
        ]

    def load_plugins(self):
        for klass in self.plugin_classes():
            self.plugins.append(klass(self.api))

class Plugin(object):
    def __init__(self, api):
        self.api = api

    # default behavior
    def process_event(self, event):
        if event['type'] == 'message':
            self.process_message(event)

    # for override
    def process_message(self, message):
        pass

# sample plugin
class EventTypePlugin(Plugin):
    def process_event(self, event):
        print 'type: %s' % event['type']

# sample plugin
class PrintPlugin(Plugin):
    def process_message(self, message):
        if 'subtype' in message:
            return
        user    = message['user_dict']
        channel = message['channel_dict']
        print '[#%s]<%s>: %s' % (channel['name'], user['name'], message['text'])

def main():
    print 'run'
    bot = SlackBot()
    bot.run()

if __name__ == '__main__':
    main()

