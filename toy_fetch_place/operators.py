
import hpn.fbch  # for Operator
import hpnutil.denotation  # for KRD fluent

from toy_fetch_place.world import *
from toy_fetch_place.world_state import *
from toy_fetch_place.primitives_and_progress import *
from toy_fetch_place.fluents import *
from toy_fetch_place.generators import *
from toy_fetch_place.heuristics_and_cost import *


go_operator = hpn.fbch.Operator(
    # Name
    'Go',
    # Arguments
    ['RobotName', 'StartLocation', 'DestinationLocation'],
    # Preconditions
    {0: {IsRobot(['RobotName'], True),
         Know([ContainerState(['DestinationLocation']), 'open', 1], True),
         Know([Location(['RobotName']), 'StartLocation', 1], True)
         },
      # 1: {Know([Location(['RobotName']), 'StartLocation', 1], True)},
     },
    # Result
    [({Know([Location(['RobotName']), 'DestinationLocation', 1], True)}, {})],
    # generators
    [GenRobotName(['RobotName'], []),
     GenGoStartLocation(['StartLocation'], ['DestinationLocation'])],
    # Primitive
    prim=goPrimitive,
    # Progress Function
    f=goProgress
)

manipulate_environment_operator = hpn.fbch.Operator(
    # Name
    'ManipulateEnvironment',
    # Arguments
    ['RobotName', 'ContainerName', 'ContainerState', 'Arm', 'CurrentContainerState'],
    # Preconditions
    {0: {
        # robotname has to be our robot
        IsRobot(['RobotName'], True),
        # the robot has to have a free hand to open the container with it
        Know([InHand(['Arm']), None, 1], True),
        # need this for calculating proper preimages
        Know([ContainerState(['ContainerName']), 'CurrentContainerState', 1], True),
        # the robot has to be standing on the floor, ideally close to the container
        Know([Location(['RobotName']), 'floor', 1], True)
    },
     # 1: {
     #    # the robot has to be standing on the floor, ideally close to the container
     #    Know([Location(['RobotName']), 'floor', 1], True)}
    },
    # Result
    [({Know([ContainerState(['ContainerName']), 'ContainerState', 1], True)}, {})],
    # generators
    [GenRobotName(['RobotName'], []),
     GenFreeArm(['Arm'], []),
     GenCurrentContainerState(['CurrentContainerState'], ['ContainerName'])],
    # Primitive
    prim=manipulateEnvironmentPrimitive,
    # Progress Function
    f=manipulateEnvironmentProgress
)

pick_up_operator = hpn.fbch.Operator(
    # Name
    'PickUp',
    # Arguments
    ['RobotName', 'Arm', 'ItemName', 'ItemLocation'],
    # Preconditions
    {0: {
        # RobotName has to be our robot
        IsRobot(['RobotName'], True),
        # the robot has to have a free hand
        Know([InHand(['Arm']), None, 1], True),
        # we're picking up the item from a certain location
        Know([Location(['ItemName']), 'ItemLocation', 1], True),
        # and robots cannot pick up other robots
        IsRobot(['ItemName'], False),
        # and the robot is at the same location as the item
        Know([Location(['RobotName']), 'ItemLocation', 1], True)
    },
     # 1: {
     #    # and the robot is at the same location as the item
     #    Know([Location(['RobotName']), 'ItemLocation', 1], True)}
     },
    # Result
    [({Know([InHand(['Arm']), 'ItemName', 0.75], True)}, {})],
    # generators
    [GenRobotName(['RobotName'], []),
     GenPickUpItemLocation(['ItemLocation'], ['ItemName'])],
    # Primitive
    prim=pickUpPrimitive,
    # Progress Function
    f=pickUpProgress
)

place_operator = hpn.fbch.Operator(
    # Name
    'Place',
    # Arguments
    ['RobotName', 'Arm', 'ItemName', 'ItemLocation'],
    # Preconditions
    {0: {
        # RobotName has to be the name of our robot
        IsRobot(['RobotName'], True),
        # the item we're placing has to be in robot's hand
        Know([InHand(['Arm']), 'ItemName', 1], True),
        # robots cannot place other robots
        IsRobot(['ItemName'], False),
        # we have to know where we want to place the item.
        # this is not the case if we just want to free up an arm,
        # but for now we will not support this, it's a difficult task to find out
        # where to intermediately dispose of an object
        # hpnutil.denotation.KRD(['ItemLocation'], True)  <-- somehow didn't work, not the right way to use it?
        # so we will only support placing an object there where the robot is currently standing
        Know([Location(['RobotName']), 'ItemLocation', 1], True)
    },
     # 1: {
     #    # we have to know where we want to place the item.
     #    # this is not the case if we just want to free up an arm,
     #    # but for now we will not support this, it's a difficult task to find out
     #    # where to intermediately dispose of an object
     #    # hpnutil.denotation.KRD(['ItemLocation'], True)  <-- somehow didn't work, not the right way to use it?
     #    # so we will only support placing an object there where the robot is currently standing
     #    Know([Location(['RobotName']), 'ItemLocation', 1], True)}
    },
    # Result
    [({Know([Location(['ItemName']), 'ItemLocation', 0.75], True)}, {}),
     ({Know([InHand(['Arm']), None, 0.75], True)}, {})
     ],
    # generators
    [GenRobotName(['RobotName'], []),
     GenPlaceLocation(['ItemLocation'], []),
     GenPlaceArm(['Arm'], ['ItemName']),
     GenPlaceItemName(['ItemName'], ['Arm'])],
    # Primitive
    prim=placePrimitive,
    # Progress Function
    f=placeProgress
)

# regrasp_operator = hpn.fbch.Operator(
#     # Name
#     'Regrasp',
#     # Arguments
#     ['CurrentArm', 'NewArm', 'ItemName'],
#     # Preconditions
#     {0: {Know([InHand(['CurrentArm']), 'ItemName', 0.75], True),
#          Know([InHand(['NewArm']), None, 1.0], True)}},
#     # Result
#     [({Know([InHand(['NewArm']), 'ItemName', 0.75], True)}, {}),
#      ({Know([InHand(['CurrentArm']), None, 0.75], True)}, {})],
#     # generators
#     [GenRegraspNewArm(['NewArm', 'ItemName'], ['CurrentArm']),
#      GenRegraspCurrentArm(['CurrentArm'], ['NewArm', 'ItemName']),
#     ],
#     # Primitive
#     prim=regraspPrimitive,
#     # Progress Function
#     f=regraspProgress
# )

examine_environment_operator = hpn.fbch.Operator(
    # Name
    'ExamineEnvironment',
    # Arguments
    ['ItemName', 'ItemLocation', 'ProbabilityBefore', 'RobotName'],
    # Preconditions
    {0: {Know([Location(['ItemName']), 'ItemLocation', 'ProbabilityBefore'], True),
         IsRobot(['RobotName'], True),
         Know([Location(['RobotName']), 'ItemLocation', 1], True)
         },
     # 1: {IsRobot(['RobotName'], True),
     #     Know([Location(['RobotName']), 'ItemLocation', 1], True)}
     },
    # Result
    [({Know([Location(['ItemName']), 'ItemLocation', 1], True)}, {})],
    # generators
    [GenExamineRegressProb(['ProbabilityBefore'], []),
     GenRobotName(['RobotName'], [])],
    # Primitive
    prim = examinePrimitive,
    # Progress Function
    f = examineProgress
)

examine_hand_operator = hpn.fbch.Operator(
    # Name
    'ExamineHand',
    # Arguments
    ['ItemName', 'Arm', 'ProbabilityBefore'],
    # Preconditions
    {0 : {Know([InHand(['Arm']), 'ItemName', 'ProbabilityBefore'], True)}},
    # Result
    [({Know([InHand(['Arm']), 'ItemName', 1], True)}, {})],
    # generators
    [GenExamineRegressProb(['ProbabilityBefore'], [])],
    # Primitive
    prim = examinePrimitive,
    # Progress Function
    f = examineProgress
)