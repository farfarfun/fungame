"""
comment
"""

import json
from datetime import datetime

from farlog import getLogger

from fungame.games.topwar.core.db import PlayerBaseInfo, ResourceInfo
from fungame.games.topwar.entity import ActionInterface, ActionRequest, ActionResponse

logger = getLogger("fungame")


class PrintAction(ActionInterface):
    """记录 Top War 响应的调试动作。"""

    def __init__(self) -> None:
        """初始化动作。

        :return: 无。
        """
        super().__init__()

    def run(self, response: ActionResponse) -> None:
        """记录收到的响应。

        :param response: 要记录的游戏协议响应。
        :return: 无。
        """
        logger.info(response)


class MapInfoAction(ActionInterface):
    """处理地图信息响应，并同步玩家和资源数据。"""

    def __init__(self) -> None:
        """初始化地图数据存储。

        :return: 无。
        """
        self.player_db = PlayerBaseInfo()
        self.resource_db = ResourceInfo()
        super().__init__()

    @staticmethod
    def request(
        x: int = 100,
        y: int = 100,
        k: int = 1554,
        width: int = 7,
        height: int = 16,
        march_info: bool = True,
    ) -> ActionRequest:
        """构造查询地图区块信息的请求。

        :param x: 区块起始横坐标。
        :param y: 区块起始纵坐标。
        :param k: 目标游戏服 ID。
        :param width: 区块宽度。
        :param height: 区块高度。
        :param march_info: 是否返回行军信息。
        :return: 地图信息请求对象。
        """
        p = {
            "x": x,
            "y": y,
            "k": k,
            "width": width,
            "height": height,
            "marchInfo": march_info,
        }
        return ActionRequest(cid=901, o="242", p=p)

    def run(self, response: ActionResponse) -> None:
        """处理地图响应并写入资源库。

        :param response: 服务端返回的地图信息响应。
        :return: 无。
        """
        if response.cid == 901:
            self.load_point(response.data)

    def load_point(self, point_json: str) -> None:
        """解析地图点位并保存玩家及资源记录。

        :param point_json: 包含 ``pointList`` 的 JSON 文本。
        :return: 无。
        :raises json.JSONDecodeError: 当点位数据不是合法 JSON 时抛出。
        :raises KeyError: 当点位数据缺少必要字段时抛出。
        """
        point_json = json.loads(point_json)
        for point in point_json["pointList"]:
            point_type = point["pointType"]

            if point_type == 1:
                self.player_db.add_player(point)
            elif point_type in [4, 38]:
                if "playerInfo" in point["r"]:
                    self.resource_db.add_resource(point)
            else:
                if "playerInfo" in json.dumps(point):
                    pass

    def clear(self) -> None:
        """删除已过期的资源记录。

        :return: 无。
        """
        sql = f"DELETE FROM {self.resource_db.table_name} WHERE expire_time<{int(datetime.now().timestamp())};"
        self.resource_db.execute(sql)
