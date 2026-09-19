from farlog import getLogger

from fungame.games.topwar.action import MapInfoAction, PrintAction
from fungame.games.topwar.server.action import TopWarAction

logger = getLogger("fungame")

ping_interval = 30


def main():
    """启动 topwar 地图巡查任务（需要预先在 funsecret 中配置好账号 token）"""
    topwar = TopWarAction()
    topwar.add_action(PrintAction())
    topwar.add_action(MapInfoAction())
    topwar.run()
    logger.info("It is your show time.")
    topwar.map_walk()


if __name__ == "__main__":
    main()
