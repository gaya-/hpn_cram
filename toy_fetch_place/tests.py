
import hpn.fbch  # for State and HPN

from toy_fetch_place.world import *
from toy_fetch_place.world_state import *
from toy_fetch_place.operators import *


########################## Tests ########################

def test():
    cup = Item('cup_1', 'cup')
    bowl = Item('bowl_1', 'bowl')
    spoon = Item('spoon_1', 'spoon')
    cereal = Item('cereal_1', 'cereal')
    milk = Item('milk_1', 'milk')

    robot = Robot('pr2', {'left_arm': milk})

    environment = Environment('kitchen',
                              {'sink_drawer_middle': [cup, bowl],
                               'sink_drawer_upper': [spoon],
                               'oven_vertical_drawer_right': [cereal],
                               # 'fridge': [milk],
                               'floor': [robot]})

    # fail_probabilities = {'Fetch': 0.5, 'Deliver': 0.5, 'Access': 0.2, 'Reset': 0.2, 'Detect': 0}
    fail_probabilities = {}

    world = World(environment, robot, fail_probabilities)
    world.draw()

    world_state = WorldState.to_world_state(world)
    starting_state = hpn.fbch.State([], world_state)
    goal_state = hpn.fbch.State([Location(['pr2'], 'fridge')])
    # goal_state = hpn.fbch.State([ContainerState(['fridge'], 'open')])
    # goal_state = hpn.fbch.State([InHand(['left_arm'], 'spoon_1')])
    # goal_state = hpn.fbch.State([Location(['milk_1'], 'fridge')])
    # goal_state = hpn.fbch.State([Location(['spoon_1'], 'sink_drawer_lower'),
    #                              Location(['bowl_1'], 'sink_drawer_lower')])

    hpn.fbch.HPN(starting_state, goal_state,
                 [go_operator, manipulate_environment_operator, pick_up_operator, place_operator], #, regrasp_operator],
                 world,
                 fileTag='test_visualization', hpnFileTag='test_visualization')


test()
