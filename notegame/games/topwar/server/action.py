import json
import time
from threading import Thread
from typing import List

import pandas as pd
from notegame.games.topwar.action import MapInfoAction
from notegame.games.topwar.entity import (ActionInterface, ActionRequest,
                                          ActionResponse)
from tqdm import tqdm
from websocket import WebSocket, create_connection

ping_interval = 30


class TopWarAction:
    def __init__(self, token=None, version="1.231.2", server_id=1554, web_socket=None):
        self.web_socket = web_socket or f"wss://server-knight-s1200.rivergame.net/s{server_id}"
        self.ws: WebSocket = create_connection(self.web_socket)
        self.action_list: List[ActionInterface] = []
        self.oid = -1
        self.map_info = None

        # self.token = read_secret(value=token, cate1='notechats', cate2='notegame', cate3='topwar', cate4='user',
        #                          cate5='token')
        # self.version = version
        # self.server_id = server_id
        self.login_request = ActionRequest.login(server_id=server_id, version=version, token=token)

    def get_oid(self):
        self.oid += 1
        return str(self.oid)

    def run(self):
        print('connection established')
        self.send_request(self.login_request)

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
                    for action in self.action_list:
                        action.run(response)
                except Exception as e:
                    print(f'error:{e}\t{msg}')

        Thread(target=on_message).start()
        time.sleep(5)

    def send_request(self, request: ActionRequest):
        request.o = self.get_oid()
        msg = request.__str__()
        try:
            self.ws.send(msg)
        except Exception as e:
            print(f'{e}:{msg}')

    def add_action(self, action: ActionInterface):
        self.action_list.append(action)

    def map_walk(self, step=20, width=480, height=980, sleep_time=1):
        # for i, j in tqdm(spiral_traverse(start_row=step, start_col=step,
        #                                  end_row=width, end_col=height,
        #                                  stepx=step, stepy=step * 2)):
        for i in tqdm(range(step, width, step)):
            for j in range(step, height, step * 2):
                req = MapInfoAction.request(x=i, y=j, width=step, height=step * 2, k=1554)
                self.send_request(req)
                time.sleep(sleep_time)

    def search(self, user_name=None, pid=None):
        if self.map_info is None:
            for action in self.action_list:
                if isinstance(action, MapInfoAction):
                    self.map_info = action
                    break
        if self.map_info is None:
            self.map_info = MapInfoAction()

        condition = {"user_name": user_name, "pid": pid}

        user_infos = pd.DataFrame.from_dict(self.map_info.player_db.select(condition=condition))
        resource_infos = pd.DataFrame.from_dict(self.map_info.resource_db.select(condition=condition))

        res = ""
        if len(user_infos) == 1:
            user_info = json.loads(user_infos.to_json(orient='records'))[0]
            res = f"{user_info['user_name']}:({user_info['x']},{user_info['y']})"

        if len(resource_infos) > 0:
            for resource_info in json.loads(resource_infos.to_json(orient='records')):
                res = f"{res}\t({resource_info['item_name']},{resource_info['x']},{resource_info['y']})"
        return res
