import json

from notegame.games.topwar.entity.base_enum import ActionEnum
from notetool.secret import read_secret


class ActionRequest:
    def __init__(self, cid=None, o=None, p=None):
        self.cid = cid
        self.o = o
        self.p = p or {}

    @staticmethod
    def login(token=None, version="1.231.2", server_id=1554):
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
    def map_search(min_level=78, max_level=85, group_type=42, point_type=1):
        p = {"minLevel": min_level, "maxLevel": max_level, "groupType": group_type, "pointType": point_type}
        return ActionRequest(cid=906, o='0', p=p)

    @staticmethod
    def hero_list():
        p = {}
        return ActionRequest(cid=861, o="4", p=p)

    @staticmethod
    def map_info(x=100, y=100, k=1554, width=7, height=16, march_info=True):
        p = {"x": x, "y": y, "k": k, "width": width, "height": height, "marchInfo": march_info}
        return ActionRequest(cid=901, o="242", p=p)

    @staticmethod
    def march_battle(x, y, p=None):
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
    def item_consume(item_id=600002, amount=1):
        p = {"itemid": item_id, "amount": amount}
        return ActionRequest(cid=815, o='0', p=p)

    @staticmethod
    def gift_code_exchange(code):
        p = {"code": code}
        return ActionRequest(cid=ActionEnum.action_695.cid, o='0', p=p)

    def __str__(self):
        # res = {"c": self.cid, "o": str(self.o), "p": json.dumps(self.p)}
        res = {"c": self.cid, "o": str(self.o), "p": self.p}
        return json.dumps(res)
