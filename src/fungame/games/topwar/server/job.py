from fungame.games.topwar.action import MapInfoAction, PrintAction
from fungame.games.topwar.server.action import TopWarAction

ping_interval = 30

topwar = TopWarAction()
topwar.add_action(PrintAction())
topwar.add_action(MapInfoAction())
topwar.run()
print("It is your show time.")
topwar.map_walk()
