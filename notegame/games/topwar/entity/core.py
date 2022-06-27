import json
from datetime import datetime


class User:
    def __init__(self, msg_data=None):
        self.fan = None
        self.fat = None

        self.uid = None
        self.uuid = None
        self.nickname = None
        self.user_name = None
        self.user_gender = None

        self.parse_from_msg(msg_data)

    def parse_from_msg(self, data=None):
        if data is None:
            return
        self.fan = data['fan']
        self.fat = data['fat']
        self.uid = data['uid']
        self.uuid = data['uuid']
        self.nickname = data['fp']['nickname']
        self.user_name = data['fp']['username']
        self.user_gender = data['fp']['usergender']

    def __str__(self):
        return f'{self.uid}\t{self.uuid}\t{self.fat}\t{self.user_name}'


class ActionInterface:
    def __init__(self, topwar=None, *args, **kwargs):
        self.topwar = topwar

    def run(self, response):
        pass
