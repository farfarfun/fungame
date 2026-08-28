import json
from datetime import datetime

from .core import User


class ActionResponse:
    def __init__(self, data=None):
        self.cid = None
        self.data = None
        self.time = None
        self.s = None
        self.o = None

        self.parse(data)

    def parse(self, data=None):
        if data is None:
            return

        data = json.loads(data)

        if len(set(data.keys()) - set('c,s,d,t,o'.split(','))) > 0:
            print(data.keys())

        self.cid = data['c']
        self.data = data['d'] or ''
        self.time = datetime.fromtimestamp(data['t'] / 1000.)
        self.s = data['s']
        self.o = data['o']

    def __str__(self):
        return f'{self.time}\t{self.cid}\t{self.s}\t{len(self.data)}'


class MessageResponse:
    def __init__(self, data=None):
        self.content = None

        self.room_id = None
        self.time = None
        self.user = User()
        self.parse(data)

    def parse(self, data=None):
        data = json.loads(data)[1]
        data['fp'] = json.loads(data['fp'])
        self.time = datetime.fromtimestamp(data['time'] / 1000.)
        self.room_id = data['roomId']
        self.content = data['content']
        self.user.parse_from_msg(data)

    def __str__(self):
        return f'{self.time}\t{self.user}:\t{self.content}'
