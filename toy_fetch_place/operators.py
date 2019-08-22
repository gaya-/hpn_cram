
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
         Location(['RobotName'], 'StartLocation'),
         ContainerState(['DestinationLocation'], 'open')
         },
     # 1: {Location(['RobotName'], 'StartLocation')},
     # 2: {ContainerState(['DestinationLocation'], 'open')}
     },
    # Result
    [({Location(['RobotName'], 'DestinationLocation')}, {})],
    # generators
    [GenRobotName(['RobotName'], [])],
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
        # the robot has to be standing on the floor, ideally close to the container
        Location(['RobotName'], 'floor'),
        # and has to have a free hand to open the container with it
        InHand(['Arm'], None),
        # need this for calculating proper preimages
        ContainerState(['ContainerName'], 'CurrentContainerState')}},
    # Result
    [({ContainerState(['ContainerName'], 'ContainerState')}, {})],
    # generators
    [GenRobotName(['RobotName'], []),
     GenFreeArm(['Arm'], [])],
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
        InHand(['Arm'], None),
        # we're picking up the item from a certain location
        Location(['ItemName'], 'ItemLocation'),
        # and the robot is at the same location
        Location(['RobotName'], 'ItemLocation'),
        # and robots cannot pick up other robots
        IsRobot(['ItemName'], False)},
     # 1: {Location(['RobotName'], 'ItemLocation')}
     },
    # Result
    [({InHand(['Arm'], 'ItemName')}, {})],
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
    ['RobotName', 'Arm', 'ItemName', 'RobotLocation'],
    # Preconditions
    {0: {
        # RobotName has to be the name of our robot
        IsRobot(['RobotName'], True),
        # the item we're placing has to be in robot's hand
        InHand(['Arm'], 'ItemName'),
        # robots cannot place other robots
        IsRobot(['ItemName'], False),
        # we have to know where we want to place the item.
        # this is not the case if we just want to free up an arm,
        # but for now we will not support this, it's a difficult task to find out
        # where to intermediately dispose of an object
        # hpnutil.denotation.KRD(['ItemLocation'], True)  <-- somehow didn't work, not the right way to use it?
        # so we will only support placing an object there where the robot is currently standing
        Location(['RobotName'], 'RobotLocation')
    },
     # 1: {Location(['RobotName'], 'ItemLocation')}
    },
    # Result
    [({Location(['ItemName'], 'RobotLocation')}, {}),
      ({InHand(['Arm'], None)}, {})
     ],
    # generators
    [GenRobotName(['RobotName'], []),
     GenPlaceLocation(['RobotLocation'], []),
     GenPlaceArm(['Arm'], ['ItemName'])],
    # Primitive
    prim=placePrimitive,
    # Progress Function
    f=placeProgress
)

regrasp_operator = hpn.fbch.Operator(
    # Name
    'Regrasp',
    # Arguments
    ['CurrentArm', 'NewArm', 'ItemName'],
    # Preconditions
    {0: {#Location(['ItemName'], 'CurrentArm'),
         InHand(['CurrentArm'], 'ItemName'),
         InHand(['NewArm'], None)}},
    # Result
    [({InHand(['NewArm'], 'ItemName')}, {}),
     ({InHand(['CurrentArm'], None)}, {})],
    # generators
    [GenRegraspNewArm(['NewArm', 'ItemName'], ['CurrentArm']),
     GenRegraspCurrentArm(['CurrentArm'], ['NewArm', 'ItemName']),
    ],
    # Primitive
    prim=regraspPrimitive,
    # Progress Function
    f=regraspProgress
)