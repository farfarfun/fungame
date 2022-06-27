from notegame.games.topwar.entity.base import Action, Item, Resource


class ItemEnum:
    item_600001 = Item(600001, name="大体力瓶")
    item_600002 = Item(600002, name="大体力瓶")
    item_910005 = Item(910005, name='玉米')

    def __init__(self):
        pass


class ActionEnum:
    action_695 = Action(695, "礼品码", example='"p": {"code": "AUC"}')
    action_11016 = Action(11016, "队列的设置", example='')

    def __init__(self):
        pass


class ResourceEnum:
    resource_102 = Resource(502, "1级金")
    resource_103 = Resource(503, "2级金")
    resource_104 = Resource(504, "3级金")
    resource_105 = Resource(505, "4级金")
    resource_106 = Resource(506, "5级金")

    resource_502 = Resource(502, "1级田")
    resource_503 = Resource(503, "2级田")
    resource_504 = Resource(504, "3级田")
    resource_505 = Resource(505, "4级田")
    resource_506 = Resource(506, "5级田")

    resource_702 = Resource(702, "1级油")
    resource_703 = Resource(703, "2级油")
    resource_704 = Resource(704, "3级油")
    resource_705 = Resource(705, "4级油")
    resource_706 = Resource(706, "5级油")

    resource_1501 = Resource(706, "6级油")
    resource_1502 = Resource(706, "6级田")
    resource_1503 = Resource(706, "6级金")

    def __init__(self):
        pass
