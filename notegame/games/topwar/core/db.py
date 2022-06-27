import json
import os
from datetime import datetime

from notedrive.tables import SqliteTable
from notegame.games.topwar.utils import merge_info
from notetool.secret import read_secret


class BaseInfo(SqliteTable):
    def __init__(self, db_path=None, *args, **kwargs):
        if db_path is None:
            db_path = read_secret(cate1="local", cate2="game", cate3="topwar", cate4="db_path")
        if db_path is None:
            db_path = os.path.abspath(os.path.dirname(__file__)) + '/db/topwar.accdb'
        super(BaseInfo, self).__init__(db_path=db_path, *args, **kwargs)


class PlayerBaseInfo(BaseInfo):
    def __init__(self, table_name='playerBaseInfo', *args, **kwargs):
        super(PlayerBaseInfo, self).__init__(table_name=table_name, *args, **kwargs)
        self.columns = ['pid', 'nick_name', 'user_name', 'national_flag', 'user_gender', 'head_img_url',
                        'avatar_url', 'power', 'player_level', 'shield_time', 'fire_time', 'province',
                        'x', 'y', 'k', 'aid', 'a_tag', 'gmt']
        self.create()

    def create(self):
        self.execute(f"""
            create table if not exists {self.table_name} (               
              pid             VARCHAR(35)    primary key 
              ,nick_name      VARCHAR(100)   DEFAULT ''
              ,user_name      varchar(100)   DEFAULT ''
              ,national_flag  integer        DEFAULT 0
              ,user_gender    integer        DEFAULT 0
              ,gender         integer        DEFAULT 0
              ,head_img_url   varchar(150)   DEFAULT ''
              ,avatar_url     varchar(150)   DEFAULT ''
              ,power          varchar(50)    DEFAULT ''
              ,player_level   integer        DEFAULT 0
	          ,shield_time    integer        DEFAULT 0
	          ,fire_time      integer        DEFAULT 0
	          ,province       integer        DEFAULT 0
	          ,x              integer        DEFAULT 0
	          ,y              integer        DEFAULT 0
	          ,k              integer        DEFAULT 0
	          ,aid            integer        DEFAULT 0
	          ,a_tag          varchar(10)    DEFAULT ''
              ,gmt            varchar(20)    DEFAULT ''
              );
            """)

    def add_player(self, point: dict):
        properties = merge_info(json.loads(point['p']['playerInfo']))
        properties = merge_info(point['p'], properties=properties)
        properties = merge_info(point, properties=properties)
        conditions = {"pid": properties['pid']}
        properties.update({
            "gmt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.update_or_insert(properties, condition=conditions)


class ResourceInfo(BaseInfo):
    # 106 -5级矿
    # 706 -5级田
    # 1502-6级田
    item_dict = {
        102: "1级金",
        103: "2级金",
        104: "3级金",
        105: "4级金",
        106: "5级金",

        502: "1级油",
        503: "2级油",
        504: "3级油",
        505: "4级油",
        506: "5级油",

        702: "1级田",
        703: "2级田",
        704: "3级田",
        705: "4级田",
        706: "5级田",

        1501: "6级油",
        1502: "6级田",
        1503: "6级金"
    }

    def __init__(self, table_name='resourceBaseInfo', *args, **kwargs):
        super(ResourceInfo, self).__init__(table_name=table_name, *args, **kwargs)
        self.columns = ['id', 'owner_id', 'nick_name', 'user_name',
                        'x', 'y', 'k', 'aid', 'a_tag', 'point_type', 'expire_time', 'item_id', 'item_name', 'gmt']
        self.create()

    def create(self):
        self.execute(f"""
            create table if not exists {self.table_name} (               
              id              VARCHAR(35)    primary key 
              ,owner_id        VARCHAR(35)    DEFAULT 0
              ,nick_name      VARCHAR(100)   DEFAULT ''
              ,user_name      varchar(100)   DEFAULT ''
	          ,x              integer        DEFAULT 0
	          ,y              integer        DEFAULT 0
	          ,k              integer        DEFAULT 0
	          ,aid            integer        DEFAULT 0
	          ,a_tag          varchar(10)    DEFAULT ''
	          ,point_type     integer        DEFAULT 0
	          ,expire_time    integer        DEFAULT 0
	          ,item_id        integer        DEFAULT 0
	          ,item_name      varchar(10)    DEFAULT ''
              ,gmt            varchar(20)    DEFAULT ''
              );
            """)

    def add_resource(self, point: dict):
        properties = merge_info(json.loads(point['r']['playerInfo']))
        properties = merge_info(point['r'], properties=properties)
        properties = merge_info(point, properties=properties)
        properties['item_name'] = self.item_dict.get(properties['item_id']) or properties['item_id']

        conditions = {"id": properties['id']}
        properties.update({
            "gmt": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.update_or_insert(properties, condition=conditions)
