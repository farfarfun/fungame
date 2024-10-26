import json
import time
from threading import Thread

from notegame.games.topwar.entity import ActionResponse
from notetool.secret import read_secret
from websocket import WebSocket, create_connection

ping_interval = 30


class ActionRequest:
    def __init__(self, cid=None, o=None, p=None):
        self.cid = cid
        self.o = o
        self.p = p or {}

    @staticmethod
    def hero_list():
        p = {}

        return ActionRequest(cid=861, o="4", p=p)

    @staticmethod
    def map_info(x=299, y=463, k=1554, width=15, height=30, march_info=True):
        p = {"x": x, "y": y, "k": k, "width": width, "height": height, "marchInfo": march_info}
        # {"c":1001,"o":"81","p":{"x":299,"y":463,"k":1554,"width":10,"height":19}}
        # {"c":901,"o":"77","p":{"x":299,"y":463,"k":1554,"width":15,"height":30,"marchInfo":true}}

        return ActionRequest(cid=901, o="77", p=p)

    def __str__(self):
        res = {"c": self.cid, "o": str(self.o), "p": json.dumps(self.p)}
        return json.dumps(res)


class TopWarAction:
    def __init__(self, token=None, web_socket=None):
        self.token = read_secret(value=token, cate1='notechats', cate2='notegame', cate3='topwar', cate4='user',
                                 cate5='token')
        self.web_socket = web_socket or "wss://server-knight-s1200.rivergame.net/s1554"
        self.ws: WebSocket = create_connection(self.web_socket)
        self.ws_init()

    def ws_init(self):
        print('connection established')
        print(f'token:{self.token}')
        data = {
            "c": 1,
            "o": "0",
            "p": {
                "token": self.token,
                "country": "CN",
                "lang": "zh_cn",
                "nationalFlag": 48,
                "ip": "0",
                "pf": "android",
                "platform": "webgame",
                "channel": "webgame_webgameCn",
                "platformVer": "1.218.3",
                "containerType": "web",
                "serverId": 1554,
                "serverInfoToken": self.token,
                "appVersion": "1.218.3",
                "gaid": "",
                "itemId": ""
            }
        }
        self.ws.send(json.dumps(data))

        def start_heartbeat():
            time.sleep(ping_interval)
            self.ws.send('2')
            start_heartbeat()

        Thread(target=start_heartbeat).start()

        def on_message():
            while True:
                msg = self.ws.recv()
                try:
                    response = ActionResponse(msg)
                    print(response)
                    if response.cid == 901:
                        print(response.data)
                except Exception as e:
                    print(f'error:{e}\t{msg}')

        Thread(target=on_message).start()


topwar = TopWarAction()

topwar.ws.send(ActionRequest.map_info().__str__())
print("waiting")
