import threading
import time

import websocket
from notegame.games.topwar.entity import MessageResponse
from notetool.secret import read_secret

ping_interval = 30


class TopWarMessage:
    def __init__(self, uuid=None, topwar_channels=None, web_socket=None):
        self.ws = None
        self.uuid = read_secret(cate1='notechats', cate2='notegame', cate3='topwar', cate4='user', cate5='uuid',
                                value=uuid)
        self.web_socket = web_socket or "wss://group-push.rivergame.net/socket.io/sjzb/1554/?EIO=3&transport=websocket"
        self.topwar_channels = topwar_channels or {"alliance_666": "102_2_1554_767182",
                                                   "world_1554": "102_1_1554",
                                                   "cross": "102_3_cross_1554_1600"}

    def on_message(self, ws, response):
        """
        """
        if 'chatpush' in response:
            response = MessageResponse(response[2:])
            print(response)

    def on_open(self, ws):
        print('connection established')

        count = 420
        for key in list(self.topwar_channels.keys()):
            channel_id = self.topwar_channels[key]
            print(f'Joined {key.upper()}')
            ws.send(f'{count}["join","{channel_id}"]')
            count += 1

        print(f'Binded UUID: {self.uuid}')
        ws.send(f'{count}["bind","{self.uuid}"]')

        def start_heartbeat():
            time.sleep(ping_interval)
            ws.send('2')
            start_heartbeat()

        threading.Thread(target=start_heartbeat).start()

    def on_close(self, ws):
        print('disconnected')

    def connect_websocket(self):
        self.ws = websocket.WebSocketApp(self.web_socket,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.ws.run_forever()

    def run(self):
        self.connect_websocket()
