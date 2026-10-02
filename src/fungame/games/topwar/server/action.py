import json
import time
from threading import Thread

import pandas as pd
from farlog import getLogger
from tqdm import tqdm
from websocket import WebSocket, WebSocketException, create_connection

from fungame.games.topwar.action import MapInfoAction
from fungame.games.topwar.entity import ActionInterface, ActionRequest, ActionResponse

logger = getLogger("fungame")

ping_interval = 30


class TopWarAction:
    """Top War 游戏客户端的 WebSocket 连接封装。

    负责建立长连接、发送登录/业务请求、维持心跳，并把收到的消息分发给已注册的
    `ActionInterface` 实现去处理。
    """

    def __init__(
        self,
        token: str | None = None,
        version: str = "1.231.2",
        server_id: int = 1554,
        web_socket: str | None = None,
    ) -> None:
        """建立到 Top War 服务器的 WebSocket 连接并准备登录请求。

        :param token: 登录凭据；为 `None` 时由 `ActionRequest.login` 通过 `funsecret` 读取。
        :param version: 客户端版本号，拼进登录请求。
        :param server_id: 目标游戏服 ID，用于选择连接地址。
        :param web_socket: 显式指定 WebSocket 地址；为 `None` 时按 `server_id` 拼接默认地址。
        """
        self.web_socket = web_socket or f"wss://server-knight-s1200.rivergame.net/s{server_id}"
        self.ws: WebSocket = create_connection(self.web_socket)
        self.action_list: list[ActionInterface] = []
        self.oid = -1
        self.map_info: MapInfoAction | None = None

        self.login_request = ActionRequest.login(server_id=server_id, version=version, token=token)

    def get_oid(self) -> str:
        """生成并返回下一个自增的请求序号（`o` 字段）。

        :return: 字符串形式的自增请求序号。
        """
        self.oid += 1
        return str(self.oid)

    def run(self) -> None:
        """登录并启动心跳线程、消息监听线程，驱动整个客户端运行。

        :return: 无返回值；该方法会启动两个后台线程后立即返回（阻塞 5 秒等待连接稳定）。
        """
        logger.info("connection established")
        self.send_request(self.login_request)

        def start_heartbeat() -> None:
            """周期性发送心跳包，保持 WebSocket 连接不被服务端断开。"""
            time.sleep(ping_interval)
            self.ws.send('2')
            start_heartbeat()

        Thread(target=start_heartbeat).start()

        def on_message() -> None:
            """持续接收服务端消息并分发给已注册的 action 处理。"""
            while True:
                msg = self.ws.recv()
                try:
                    response = ActionResponse(msg)
                    for action in self.action_list:
                        action.run(response)
                except (ValueError, KeyError) as e:
                    # 单条消息解析失败不应中断长期运行的监听线程，记录完整上下文后继续处理下一条
                    logger.exception(f"处理 topwar 消息失败，已跳过: {e}\t{msg}")

        Thread(target=on_message).start()
        time.sleep(5)

    def send_request(self, request: ActionRequest) -> None:
        """为请求分配序号并通过 WebSocket 发送。

        :param request: 待发送的业务请求。
        :return: 无返回值。
        :raises RuntimeError: WebSocket 发送失败时抛出，附带原始异常作为 cause。
        """
        request.o = self.get_oid()
        msg = request.__str__()
        try:
            self.ws.send(msg)
        except WebSocketException as e:
            raise RuntimeError(f"发送 topwar 请求失败: {msg}") from e

    def add_action(self, action: ActionInterface) -> None:
        """注册一个消息处理器，`run()` 收到消息后会依次回调已注册的处理器。

        :param action: 实现了 `ActionInterface` 的处理器实例。
        :return: 无返回值。
        """
        self.action_list.append(action)

    def map_walk(self, step: int = 20, width: int = 480, height: int = 980, sleep_time: int = 1) -> None:
        """按网格遍历地图并逐格发送地图信息查询请求。

        :param step: 网格步长（横向），同时用于查询区块的宽度。
        :param width: 遍历的横向范围上限。
        :param height: 遍历的纵向范围上限。
        :param sleep_time: 每次请求之间的等待秒数，避免请求过于密集。
        :return: 无返回值；查询结果通过已注册的 `MapInfoAction` 处理器落库。
        """
        for i in tqdm(range(step, width, step)):
            for j in range(step, height, step * 2):
                req = MapInfoAction.request(x=i, y=j, width=step, height=step * 2, k=1554)
                self.send_request(req)
                time.sleep(sleep_time)

    def search(self, user_name: str | None = None, pid: int | None = None) -> str:
        """按用户名或玩家 ID 查询已扫描到的玩家位置与周边资源点。

        :param user_name: 要查询的玩家昵称；与 `pid` 二选一或都为 `None`（查询全部）。
        :param pid: 要查询的玩家 ID；与 `user_name` 二选一或都为 `None`（查询全部）。
        :return: 人类可读的查询结果字符串，未匹配到玩家时资源信息仍可能非空。
        """
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
