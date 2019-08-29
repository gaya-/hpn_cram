
import hpn.fbch  # for State and HPN
import hpn.globals # for rebindPenalty
# import hpn.hAddBack # for hAddBack :)

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

    fail_probabilities = {'Go': 0.1, 'PickUp': 0.5, 'Place': 0.4, 'Regrasp': 0.8, 'ManipulateEnvironment': 0.3}

    world = World(environment, robot, fail_probabilities)

    world_state = WorldState.to_world_state(world)
    world_state.draw()

    starting_state = hpn.fbch.State([], world_state)
    goal_states = [
        hpn.fbch.State([Know([ContainerState(['fridge']), 'open', 1], True)]),           # 0
        hpn.fbch.State([Know([Location(['pr2']), 'fridge', 1], True)]),                  # 1
        hpn.fbch.State([Know([Location(['milk_1']), 'fridge', 1], True)]),               # 2
        hpn.fbch.State([Know([InHand(['left_arm']), 'spoon_1', 1], True)]),              # 3
        hpn.fbch.State([Know([InHand(['left_arm']), 'spoon_1', 1], True),                # 4  <-- too big :(
                        Know([InHand(['right_arm']), 'cup_1', 1], True)]),
        hpn.fbch.State([Know([Location(['spoon_1']), 'kitchen_island_counter_top', 1], True)]),  # 5
        hpn.fbch.State([Know([Location(['spoon_1']), 'fridge', 1], True)]),                      # 6
        hpn.fbch.State([Know([Location(['spoon_1']), 'sink_drawer_lower', 1], True),        # 7  <-- definitely not :D
                        Know([Location(['bowl_1']), 'sink_drawer_lower', 1], True)]),
    ]

    # our perception operator relies on rebinding for probability values, so make rebinding cheaper
    hpn.globals.glob.rebindPenalty = 5

    hpn.fbch.HPN(starting_state, goal_states[7],
                 [go_operator, manipulate_environment_operator, pick_up_operator, place_operator,
                  examine_environment_operator, examine_hand_operator], #, regrasp_operator],
                 world,
                 h=false_fluents_heuristic,
                 fileTag='test_visualization', hpnFileTag='test_visualization')


test()


################### Questions ########################

# Why doesn't IsRobot prune the search tree? The goal IsRobot[spoon_1] = true is definitely false
# and there is no operator to achieve that goal, but the planner has a goal state with multiple fluents to achieve,
# so it ignores IsRobot[spoon_1] = true and prioritizes the other goals,
# so it continues searching. How to prioritize certain fluents?
# Hierarchy? Even so, other fluents come from other operators.

# Hierarchy always seems to make things worse?!??

# Why does ManipulateEnvironment have to have ContainerState(ContainerCurrentState) as precondition?
# Otherwise it keeps trying to execute ManipulateEnvironment time and time again one after another,
# even though the operator succeeds.
# The plan simply gives ManipulateEnvironment as the next operator according to the plan.

# How to make sure that we don't invalidate previous preconditions, e.g., InHand[x] = None sometimes
# overwrites InHand[x] = Item. HPN realizes that during execution and replans.
# But can we prevent this at planning time? That it realizes, oh, I'm overwriting, this is an invalid transition.

# How to close the drawers after done with them?? Where should this go? Precondition? Result? Which operator?
# Especially, how to close the drawer immediately after done with them. Not just at the end of the whole plan.

# How does one decide which generators one needs? For example, in Place operator, there are 3 deciding parameters:
# arm, object and place_location. Does one need generators for each of these?
# How does one decide the input of the generators then?

# Rebind cost Per operator or even argument?


################ TODOs ######################

# Define Open and Close as separate operators, at least because they have different fail probabilities

# Get rid of container state confidence, there's no perception for container states, so there's no point

# In examine progress functions, when found an object somewhere, say that Know(Location(Object), SomewhereElse, 0) = true

# Dual-arm grasping oh gosh...