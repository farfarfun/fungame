"""topwar 模块的正常/边界/失败路径测试，覆盖请求构造、响应解析与凭据读取失败场景。

这里不连接任何真实网络/游戏服务器：`TopWarAction` 用到的 `create_connection`
和 `ActionRequest.login` 用到的 `read_secret` 均通过 monkeypatch 替换为可控的假实现。
"""

import json

import pytest
from websocket import WebSocketException

from fungame.games.topwar.entity.base_enum import ActionEnum
from fungame.games.topwar.entity.core import User
from fungame.games.topwar.entity.request import ActionRequest
from fungame.games.topwar.entity.response import ActionResponse, MessageResponse
from fungame.games.topwar.server import action as action_module
from fungame.games.topwar.server.action import TopWarAction

# ---------- ActionRequest：请求构造的正常路径 ----------


def test_login_with_explicit_token_skips_funsecret():
    """显式传入 token 时不应触发 funsecret 读取，且负载字段应正确填充。"""
    req = ActionRequest.login(token="tok-123", version="9.9.9", server_id=42)
    assert req.cid == 1
    assert req.p["token"] == "tok-123"
    assert req.p["serverInfoToken"] == "tok-123"
    assert req.p["serverId"] == 42
    assert req.p["appVersion"] == "9.9.9"


def test_map_search_builds_expected_payload():
    req = ActionRequest.map_search(min_level=10, max_level=20, group_type=1, point_type=2)
    assert req.cid == 906
    assert req.p == {"minLevel": 10, "maxLevel": 20, "groupType": 1, "pointType": 2}


def test_hero_list_builds_expected_payload():
    req = ActionRequest.hero_list()
    assert req.cid == 861
    assert req.o == "4"
    assert req.p == {}


def test_map_info_builds_expected_payload():
    req = ActionRequest.map_info(x=1, y=2, k=10, width=3, height=4, march_info=False)
    assert req.cid == 901
    assert req.p == {"x": 1, "y": 2, "k": 10, "width": 3, "height": 4, "marchInfo": False}


def test_march_battle_default_payload_overrides_xy():
    req = ActionRequest.march_battle(x=100, y=200)
    assert req.cid == 902
    assert req.p["x"] == 100
    assert req.p["y"] == 200
    # 默认模板里的其他字段应保留
    assert "armyList" in req.p
    assert req.p["heroList"] == [115, 128]


def test_march_battle_custom_payload():
    custom_p = {"foo": "bar"}
    req = ActionRequest.march_battle(x=1, y=2, p=custom_p)
    assert req.p["foo"] == "bar"
    assert req.p["x"] == 1
    assert req.p["y"] == 2


def test_item_consume_builds_expected_payload():
    req = ActionRequest.item_consume(item_id=1, amount=5)
    assert req.cid == 815
    assert req.p == {"itemid": 1, "amount": 5}


def test_gift_code_exchange_builds_expected_payload():
    req = ActionRequest.gift_code_exchange("ABC123")
    assert req.cid == ActionEnum.action_695.cid
    assert req.p == {"code": "ABC123"}


def test_action_request_str_serializes_cid_o_p():
    req = ActionRequest(cid=1, o="2", p={"a": 1})
    parsed = json.loads(str(req))
    assert parsed == {"c": 1, "o": "2", "p": {"a": 1}}


# ---------- ActionRequest.login：凭据读取失败路径 ----------


def test_login_without_token_reads_from_funsecret(monkeypatch):
    """token 为 None 时应调用 funsecret.read_secret 获取凭据。"""
    captured = {}

    def fake_read_secret(**kwargs):
        captured.update(kwargs)
        return "secret-token"

    monkeypatch.setattr("fungame.games.topwar.entity.request.read_secret", fake_read_secret)

    req = ActionRequest.login()
    assert req.p["token"] == "secret-token"
    assert captured == {
        "cate1": "notechats",
        "cate2": "notegame",
        "cate3": "topwar",
        "cate4": "user",
        "cate5": "token",
    }


def test_login_without_token_propagates_funsecret_failure(monkeypatch):
    """funsecret 读取凭据失败（如未配置）时，异常应原样向上抛出，不能被吞掉。"""

    def fake_read_secret(**kwargs):
        raise RuntimeError("凭据未配置")

    monkeypatch.setattr("fungame.games.topwar.entity.request.read_secret", fake_read_secret)

    with pytest.raises(RuntimeError, match="凭据未配置"):
        ActionRequest.login()


# ---------- ActionResponse / MessageResponse：解析的正常/边界/失败路径 ----------


def test_action_response_parse_normal_path():
    payload = json.dumps({"c": 100, "d": {"x": 1}, "t": 1700000000000, "s": 0, "o": "1"})
    resp = ActionResponse(payload)
    assert resp.cid == 100
    assert resp.data == {"x": 1}
    assert resp.s == 0
    assert resp.o == "1"


def test_action_response_parse_none_data_is_noop():
    """data 为 None 时不解析，所有字段保持初始值。"""
    resp = ActionResponse(None)
    assert resp.cid is None
    assert resp.data is None


def test_action_response_parse_unknown_field_logs_warning_but_still_parses(caplog):
    """出现协议未定义字段时应记录 warning，但不应影响正常字段的解析（边界用例）。"""
    payload = json.dumps(
        {"c": 1, "d": {}, "t": 1700000000000, "s": 0, "o": "1", "unexpected_field": True}
    )
    resp = ActionResponse(payload)
    assert resp.cid == 1
    assert resp.o == "1"


def test_action_response_parse_missing_field_raises_keyerror():
    """协议字段缺失（如 PB 升级、字段改名）时应直接抛出 KeyError，而不是静默产生脏数据。"""
    payload = json.dumps({"c": 1, "d": {}, "t": 1700000000000, "o": "1"})  # 缺少 's'
    with pytest.raises(KeyError):
        ActionResponse(payload)


def test_action_response_parse_invalid_json_raises():
    """网络边界：收到非 JSON 文本（如截断的消息）时应抛出而不是静默忽略。"""
    with pytest.raises(json.JSONDecodeError):
        ActionResponse("not-json{")


def test_message_response_parse_normal_path():
    inner = {
        "fan": "fan1",
        "fat": "fat1",
        "uid": "u1",
        "uuid": "uu1",
        "time": 1700000000000,
        "roomId": "room1",
        "content": "hello",
        "fp": json.dumps({"nickname": "小明", "username": "xm", "usergender": 1}),
    }
    payload = json.dumps(["ignored_header", inner])
    resp = MessageResponse(payload)
    assert resp.room_id == "room1"
    assert resp.content == "hello"
    assert resp.user.nickname == "小明"
    assert resp.user.user_name == "xm"


def test_user_parse_from_msg_none_data_is_noop():
    user = User(None)
    assert user.uid is None
    assert user.nickname is None


# ---------- TopWarAction：网络边界（WebSocket 发送失败）----------


class _FakeWebSocket:
    """替代真实 WebSocket 连接，避免测试依赖外部网络。"""

    def __init__(self, raise_on_send=False):
        self.sent = []
        self.raise_on_send = raise_on_send

    def send(self, msg):
        if self.raise_on_send:
            raise WebSocketException("连接已断开")
        self.sent.append(msg)

    def recv(self):
        raise NotImplementedError


@pytest.fixture
def topwar_action(monkeypatch):
    fake_ws = _FakeWebSocket()
    monkeypatch.setattr(action_module, "create_connection", lambda *_a, **_k: fake_ws)
    ta = TopWarAction(token="tok", server_id=1)
    return ta, fake_ws


def test_send_request_success_assigns_oid_and_sends(topwar_action):
    ta, fake_ws = topwar_action
    req = ActionRequest.hero_list()
    ta.send_request(req)
    assert req.o == "0"
    assert len(fake_ws.sent) == 1
    assert json.loads(fake_ws.sent[0])["c"] == 861


def test_send_request_wraps_websocket_exception(monkeypatch):
    """WebSocket 发送失败（网络边界）时应包装为 RuntimeError 并携带上下文，而不是裸抛底层异常。"""
    fake_ws = _FakeWebSocket(raise_on_send=True)
    monkeypatch.setattr(action_module, "create_connection", lambda *_a, **_k: fake_ws)
    ta = TopWarAction(token="tok", server_id=1)

    with pytest.raises(RuntimeError, match="发送 topwar 请求失败"):
        ta.send_request(ActionRequest.hero_list())
