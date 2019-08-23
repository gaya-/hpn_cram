
from toy_fetch_place.world import *
from toy_fetch_place.world_state import *


# # # # # # # # # # # # # Primitives # # # # # # # # # # # # #

def manipulateEnvironmentPrimitive(operator_arguments, world_state):
    # operator_arguments = ['RobotName', 'ContainerName', 'ContainerState', 'Arm', 'CurrentContainerState']
    return [operator_arguments[1], operator_arguments[4], operator_arguments[2]]


def goPrimitive(operator_arguments, world_state):
    # operator_arguments = ['RobotName', 'StartLocation', 'DestinationLocation']
    return operator_arguments


def pickUpPrimitive(operator_arguments, world_state):
    # operator_arguments = ['RobotName', 'Arm', 'ItemName', 'ItemLocation']
    return [operator_arguments[2], operator_arguments[3], operator_arguments[1]]


def placePrimitive(operator_arguments, world_state):
    # operator_arguments = ['RobotName', 'Arm', 'ItemName', 'ItemLocation']
    return [operator_arguments[2], operator_arguments[1], operator_arguments[3]]


def regraspPrimitive(operator_arguments, world_state):
    # operator_arguments = ['CurrentArm', 'NewArm', 'ItemName']
    return [operator_arguments[2], operator_arguments[0], operator_arguments[1]]


def examinePrimitive(operator_arguments, world_state):
    # operator_arguments = ['ItemName', 'ItemLocation']
    return operator_arguments[1]

# # # # # # # # # # # # # Belief Progress Functions # # # # # # # # # # # # #

def manipulateEnvironmentProgress(world_state, operator_arguments, observations):
    # operator_arguments = ['RobotName', 'ContainerName', 'ContainerState']
    world_state.manipulate_environment(operator_arguments[1], observations)


def goProgress(world_state, operator_arguments, observations):
    # operator_arguments = ['RobotName', 'StartLocation', 'DestinationLocation']
    world_state.move_item_or_robot(operator_arguments[0], operator_arguments[1], observations)


def pickUpProgress(world_state, operator_arguments, observations):
    # operator_arguments = ['RobotName', 'Arm', 'ItemName', 'ItemLocation']
    world_state.move_item_or_robot(operator_arguments[2], operator_arguments[3], observations)


def placeProgress(world_state, operator_arguments, observations):
    # operator_arguments = ['RobotName', 'Arm', 'ItemName', 'ItemLocation']
    world_state.move_item_or_robot(operator_arguments[2], operator_arguments[1], observations)


def regraspProgress(world_state, operator_arguments, observations):
    # operator_arguments = ['CurrentArm', 'NewArm', 'ItemName']
    world_state.move_item_or_robot(operator_arguments[2], operator_arguments[0], observations)


def examineProgress(world_state, operator_arguments, observations):
    [item_name, item_location] = operator_arguments
    list_of_item_names = observations
    if item_name in list_of_item_names:
        # the item is indeed there
        # remove item from current location
        current_item_location = world_state.get_item_locations(item_name)[0]
        # perception can teleport objects, and things can disappear from closed drawers, thus, we use low-level setters
        if current_item_location in world_state.environment.possible_locations:
            # item was in the environment
            world_state.environment.items_at_locations[current_item_location] =\
                [it for it in world_state.environment.items_at_locations[current_item_location] if it.name != item_name]
        elif current_item_location in world_state.robot.possible_arms:
            # item was in robot's hand
            world_state.robot.items_in_hands[current_item_location] = None
        # add the item to the observed location
        item = world_state.get_item_with_name(item_name)
        if item_location in world_state.environment.possible_locations:
            # item is in the environment
            world_state.environment.items_at_locations[item_location].append(item)
        elif item_location in world_state.robot.possible_arms:
            # item is in robot's hand
            world_state.robot.items_in_hands[item_location] = item
        # set the confidence to 1.0
        world_state.set_probability_of_item_at_location(item_name, current_item_location, item_location, 1.0)
    # else: say that we know the object is NOT at other locations: Know(Location(Object), SomewhereElse, 0) = true