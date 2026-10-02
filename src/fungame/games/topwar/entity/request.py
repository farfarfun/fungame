import json
from typing import Any

from funsecret import read_secret

from fungame.games.topwar.entity.base_enum import ActionEnum


class ActionRequest:
    """Top War 游戏协议的请求封装。

    每个静态方法对应一种业务请求（`cid` 标识协议号），统一通过 `__str__`
    序列化为服务端期望的 JSON 文本。
    """

    def __init__(self, cid: int | None = None, o: str | None = None, p: dict | None = None) -> None:
        """构造一个请求对象。

        :param cid: 协议号，标识请求类型。
        :param o: 请求序号，发送前会被 `TopWarAction.send_request` 重新赋值。
        :param p: 请求负载；为 `None` 时使用空字典。
        """
        self.cid = cid
        self.o = o
        self.p = p or {}

    @staticmethod
    def login(token: str | None = None, version: str = "1.231.2", server_id: int = 1554) -> "ActionRequest":
        """构造登录请求。

        :param token: 登录凭据；为 `None` 时通过 `funsecret.read_secret` 从
            `notechats/notegame/topwar/user/token` 读取。
        :param version: 客户端版本号。
        :param server_id: 目标游戏服 ID。
        :return: 登录请求对象。
        :raises Exception: 当 `token` 为空且 `funsecret` 未配置对应凭据时，
            由 `read_secret` 抛出（具体异常类型取决于 `funsecret` 的实现）。
        """
        if token is None:
            token = read_secret(cate1='notechats', cate2='notegame', cate3='topwar', cate4='user', cate5='token')
        p = {
            "token": token,
            "country": "CN",
            "lang": "zh_cn",
            "nationalFlag": 48,
            "ip": "0",
            "pf": "android",
            "platform": "webgame",
            "channel": "webgame_webgameCn",
            "platformVer": version,
            "containerType": "web",
            "serverId": server_id,
            "serverInfoToken": token,
            "appVersion": version,
            "gaid": "",
            "itemId": ""
        }
        return ActionRequest(cid=1, o='0', p=p)

    @staticmethod
    def map_search(min_level: int = 78, max_level: int = 85, group_type: int = 42, point_type: int = 1) -> "ActionRequest":
        """构造按等级/类型筛选地图资源点的查询请求。

        :param min_level: 资源点等级下限。
        :param max_level: 资源点等级上限。
        :param group_type: 资源分组类型。
        :param point_type: 资源点类型。
        :return: 对应的查询请求对象。
        """
        p = {"minLevel": min_level, "maxLevel": max_level, "groupType": group_type, "pointType": point_type}
        return ActionRequest(cid=906, o='0', p=p)

    @staticmethod
    def hero_list() -> "ActionRequest":
        """构造查询英雄列表的请求。

        :return: 对应的查询请求对象。
        """
        p = {}
        return ActionRequest(cid=861, o="4", p=p)

    @staticmethod
    def map_info(
        x: int = 100,
        y: int = 100,
        k: int = 1554,
        width: int = 7,
        height: int = 16,
        march_info: bool = True,
    ) -> "ActionRequest":
        """构造查询某个地图区块信息的请求。

        :param x: 区块起始横坐标。
        :param y: 区块起始纵坐标。
        :param k: 目标游戏服 ID。
        :param width: 区块宽度。
        :param height: 区块高度。
        :param march_info: 是否同时返回行军信息。
        :return: 对应的查询请求对象。
        """
        p = {"x": x, "y": y, "k": k, "width": width, "height": height, "marchInfo": march_info}
        return ActionRequest(cid=901, o="242", p=p)

    @staticmethod
    def march_battle(x: int, y: int, p: dict | None = None) -> "ActionRequest":
        """构造派遣部队出征某个坐标的请求。

        :param x: 出征目标横坐标。
        :param y: 出征目标纵坐标。
        :param p: 自定义请求负载；为 `None` 时使用内置的默认行军编队模板
            （仅覆盖其中的 `x`/`y` 字段）。
        :return: 对应的出征请求对象。
        """
        p = p or {
            "marchType": 5,
            "x": x,
            "y": y,
            "armyList": [
                {
                    "pos": 1,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 2,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 3,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 11,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 12,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 13,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 21,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 22,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 23,
                    "armyId": 10080,
                    "armyNum": 5
                }
            ],
            "armyListNew": [
                {
                    "pos": 1,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 2,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 3,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 11,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 12,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 13,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 21,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 22,
                    "armyId": 10080,
                    "armyNum": 6
                },
                {
                    "pos": 23,
                    "armyId": 10080,
                    "armyNum": 5
                }
            ],
            "heroList": [
                115,
                128
            ],
            "trapList": [],
            "break": 0,
            "formation": 0,
            "_ci_": {
                "x": 321,
                "y": 660
            }
        }
        p.update({
            "x": x,
            "y": y
        })
        return ActionRequest(cid=902, o='1', p=p)

    @staticmethod
    def item_consume(item_id: int = 600002, amount: int = 1) -> "ActionRequest":
        """构造消耗道具的请求。

        :param item_id: 道具 ID。
        :param amount: 消耗数量。
        :return: 对应的道具消耗请求对象。
        """
        p = {"itemid": item_id, "amount": amount}
        return ActionRequest(cid=815, o='0', p=p)

    @staticmethod
    def gift_code_exchange(code: str) -> "ActionRequest":
        """构造兑换礼包码的请求。

        :param code: 礼包兑换码。
        :return: 对应的兑换请求对象。
        """
        p = {"code": code}
        return ActionRequest(cid=ActionEnum.action_695.cid, o='0', p=p)

    def __str__(self) -> str:
        """序列化为服务端期望的 JSON 文本。

        :return: `{"c": 协议号, "o": 序号, "p": 负载}` 结构的 JSON 字符串。
        """
        res: dict[str, Any] = {"c": self.cid, "o": str(self.o), "p": self.p}
        return json.dumps(res)
