
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