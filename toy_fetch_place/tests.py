
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
    goal_states = [hpn.fbch.State([Location(['pr2'], 'fridge')]),                     # 0
                   hpn.fbch.State([ContainerState(['fridge'], 'open')]),              # 1
                   hpn.fbch.State([InHand(['left_arm'], 'spoon_1')]),                 # 2
                   hpn.fbch.State([InHand(['left_arm'], 'spoon_1'),                   # 3
                                   InHand(['right_arm'], 'cup_1')]),
                   hpn.fbch.State([Location(['milk_1'], 'fridge')]),                  # 4
                   hpn.fbch.State([Location(['spoon_1'], 'kitchen_island_counter_top')]),  # 5
                   hpn.fbch.State([Location(['spoon_1'], 'fridge')]),                 # 6
                   hpn.fbch.State([Location(['spoon_1'], 'sink_drawer_lower'),        # 7  <-- doesn't work yet
                                   Location(['bowl_1'], 'sink_drawer_lower')]),       #        search tree too big
                   ]

    hpn.fbch.HPN(starting_state, goal_states[3],
                 [go_operator, manipulate_environment_operator, pick_up_operator, place_operator], #, regrasp_operator],
                 world,
                 fileTag='test_visualization', hpnFileTag='test_visualization')


test()


# Why doesn't IsRobot prune the search tree? The goal IsRobot[spoon_1] = true is definitely false
# and there is no operator to achieve that goal, but the planner has multiple fluents to achieve,
# so it ignores IsRobot[spoon_1] = true and continues searching, although at this point I would prune that branch

# Why does ManipulateEnvironment have to have ContainerState(ContainerCurrentState) as precondition?
# Otherwise it keeps trying to execute ManipulateEnvironment time and time again one after another,
# even though the operator succeeds.
# The plan simply gives ManipulateEnvironment as the next operator according to the plan.

# How to make sure that we don't invalidate previous preconditions, e.g., InHand[x] = None sometimes
# overwrites InHand[x] = Item. HPN realizes that during execution and replans.
# But can we prevent this at planning time?

# How to close the drawers after done with them?? Where should this go? Precondition? Result? Which operator?