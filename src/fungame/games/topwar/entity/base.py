class Item:
    def __init__(self, item_id, name=None):
        self.item_id = item_id
        self.name = name


class Action:
    def __init__(self, cid, name=None, example=None):
        self.cid = cid
        self.name = name
        self.example = example


class Hero:
    def __init__(self, hid, name=None):
        self.hid = hid
        self.hero_name = name


class Resource:
    def __init__(self, rid, name=None):
        self.rid = rid
        self.name = name
