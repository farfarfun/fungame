class Item:
    """表示游戏中的物品基础信息。"""

    def __init__(self, item_id: int, name: str | None = None) -> None:
        """初始化物品。

        :param item_id: 物品 ID。
        :param name: 物品名称；未提供时为 ``None``。
        :return: 无。
        """
        self.item_id = item_id
        self.name = name


class Action:
    """表示 Top War 协议动作的基础信息。"""

    def __init__(
        self, cid: int, name: str | None = None, example: str | None = None
    ) -> None:
        """初始化动作描述。

        :param cid: 协议动作 ID。
        :param name: 动作名称；未提供时为 ``None``。
        :param example: 请求示例；未提供时为 ``None``。
        :return: 无。
        """
        self.cid = cid
        self.name = name
        self.example = example


class Hero:
    """表示游戏中的英雄基础信息。"""

    def __init__(self, hid: int, name: str | None = None) -> None:
        """初始化英雄。

        :param hid: 英雄 ID。
        :param name: 英雄名称；未提供时为 ``None``。
        :return: 无。
        """
        self.hid = hid
        self.hero_name = name


class Resource:
    """表示地图资源的基础信息。"""

    def __init__(self, rid: int, name: str | None = None) -> None:
        """初始化资源。

        :param rid: 资源 ID。
        :param name: 资源名称；未提供时为 ``None``。
        :return: 无。
        """
        self.rid = rid
        self.name = name
