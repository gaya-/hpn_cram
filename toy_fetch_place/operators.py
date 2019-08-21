
import hpn.fbch  # for Operator

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
    {0: {RobotName([], 'RobotName'),
         Location(['RobotName'], 'StartLocation')},
     1: {ContainerState(['DestinationLocation'], 'open')}},
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
    ['RobotName', 'ContainerName', 'ContainerState'],
    # Preconditions
    {0: {RobotName([], 'RobotName'),
         Location(['RobotName'], 'floor')}},
    # Result
    [({ContainerState(['ContainerName'], 'ContainerState')}, {})],
    # generators
    [GenRobotName(['RobotName'], [])],
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
    {0: {RobotName([], 'RobotName'),
         Location(['ItemName'], 'ItemLocation'),
         InHand(['Arm'], None)},
     1: {Location(['RobotName'], 'ItemLocation')}},
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
    ['RobotName', 'Arm', 'ItemName', 'ItemLocation'],
    # Preconditions
    {0: {RobotName([], 'RobotName'),
         InHand(['Arm'], 'ItemName')},
     1: {Location(['RobotName'], 'ItemLocation')}},
    # Result
    [({Location(['ItemName'], 'ItemLocation')}, {}),
      ({InHand(['Arm'], None)}, {})
     ],
    # generators
    [GenRobotName(['RobotName'], []),
     # GenPlaceItemNameAndLocation(['ItemName', 'ItemLocation'], ['Arm', 'RobotName']),
     # GenPlaceArm(['Arm'], ['ItemName'])
     ],
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