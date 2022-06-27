"""
comment
"""
import json
import logging
from datetime import datetime

from notegame.games.topwar.core.db import PlayerBaseInfo, ResourceInfo
from notegame.games.topwar.entity import (ActionInterface, ActionRequest,
                                          ActionResponse)


class PrintAction(ActionInterface):
    def __init__(self):
        super(PrintAction, self).__init__()

    def run(self, response: ActionResponse):
        logging.info(response)


class MapInfoAction(ActionInterface):
    def __init__(self):
        self.player_db = PlayerBaseInfo()
        self.resource_db = ResourceInfo()
        super(MapInfoAction, self).__init__()

    @staticmethod
    def request(x=100, y=100, k=1554, width=7, height=16, march_info=True):
        p = {"x": x, "y": y, "k": k, "width": width, "height": height, "marchInfo": march_info}
        return ActionRequest(cid=901, o="242", p=p)

    def run(self, response: ActionResponse):
        if response.cid == 901:
            self.load_point(response.data)

    def load_point(self, point_json):
        point_json = json.loads(point_json)
        for point in point_json['pointList']:
            point_type = point['pointType']

            if point_type == 1:
                self.player_db.add_player(point)
            elif point_type in [4, 38]:
                if 'playerInfo' in point['r']:
                    self.resource_db.add_resource(point)
            else:
                if 'playerInfo' in json.dumps(point):
                    pass

    def clear(self):
        sql = f'DELETE FROM {self.resource_db.table_name} WHERE expire_time<{int(datetime.now().timestamp())};'
        self.resource_db.execute(sql)
