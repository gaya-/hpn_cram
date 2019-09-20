
Descrete Fetch and Place Domain
===============================


World State
-----------

World state:
  * There is the WORLD.
  * In the world, there is the ENVIRONMENT. 
    In the environment there are locations: either counter tops or containers.
  * Locations of the environment can be "open" or "closed".
    Counter tops are always open.
    Containers not always.
  * At the locations there can be no, one or more OBJECTs (aka items).
  * A special kind of object is the ROBOT. The robot is as small as the other objects.
  * The robot has two arms: LEFT_ARM and RIGHT_ARM.
    In each arm there can be one or no objects (optionally, he can carry the same object with both arms).
    Robot cannot hold himself or other robots in his hands.

Belief:
  * There is a confidence associated with each object location.
  * There is also confidence associated with container state but because there is no perception to check it, it is always 1.0.
  * We assume the localization of the robot is perfect, so the robot location confidence is always 1.0.

The world state is drawn like this:

```
ROBOT pr2:
   left_arm:                             milk_1 (0.5)
   right_arm:                            None (0.5)
ENVIRONMENT kitchen:
   fridge(closed):                      
   sink_drawer_lower(closed):           
   sink_drawer_middle(closed):           cup_1 (0.5)   bowl_1 (0.5)  
   sink_drawer_upper(closed):            spoon_1 (0.5)  
   oven_vertical_drawer_right(closed):   cereal_1 (0.5)  
   sink_area_counter_top(open):         
   kitchen_island_counter_top(open):    
   floor(open):                          pr2 (1)  
```

Numbers on the right of item names are confidences in their assumed locations.

  
Fluents
-------

```
IsRobot(Obj) = true / false

Location(Obj) = Loc

InHand(Hand) = Obj

ContainerState(Loc) = open / closed

Know(NestedFl, Value, Prob) = true / false,
  where NestedFl can be Location, InHand or ContainerState but not IsRobot,
        Prob of 0 means "I know it is not true", 0.5 -- "I've got no idea", 
                1.0 -- "I know it's true", 0.75 -- "I suspect it's true", ...
```

Operators
---------

Robot can navigate from LocationA to LocationB with `Go`.
He can only go to LocationB if LocationB is open:

```
Go(Obj, LocA, LocB): 
res:  Know(Location(Obj), LocB, 1.0) = true
pre:  IsRobot(Obj) = true, Know(ContainerState(LocB), open, 1.0) = true,
      Know(Location(Obj), LocA, 1) = true
```

Robot can open or close containers.
He can only do so, if he has a free hand and if he's standing on the floor:

```
ManipulateEnv(RobObj, Container, GoalState, Arm, CurrState):
res:  Know(ContainerState(Container), GoalState, 1) = true
pre:  IsRobot(RobObj) = true, Know(InHand(Arm), none, 1) = true, 
      Know(ContainerState(Container), CurrState, 1) = true, Know(Location(RobObj), floor, 1) = true
```

Robot can pick up an object.
That object cannot be another robot or himself.
He also needs a free hand and he has to be at the same location as the object to reach for it.
He also has to be certain about the location of the object:

```      
PickUp(RobObj, Arm, Obj, ObjLoc):
res:  Know(InHand(Arm), Obj, 0.75) = true
pre:  IsRobot(RobObj), Know(InHand(Arm), none, 1) = true, Know(Location(Obj), ObjLoc, 1) = true,
      IsRobot(Obj) = false, Know(Location(RobObj), ObjLoc, 1) = true
```

Robot can place an object.
He has to be sure he's holding the object in the hand.
The object ends up at the same location as the robot:

```      
Place(RobObj, Arm, Obj, ObjLoc):
res:  Know(Location(Obj), ObjLoc, 0.75) = true, Know(InHand(Arm), none, 0.75) = true
pre:  IsRobot(RobObj) = true, Know(InHand(Arm), Obj, 1) = true, IsRobot(Obj) = false,
      Know(Location(RobObj), ObjLoc, 1) = true
```

Robot can examine a location in the environment.
For that, he has to be at the location he wants to examine:

```
ExamineEnv(Obj, ObjLoc, ProbBefore, RobObj):
res:  Know(Location(Obj), ObjLoc, 1) = true
pre:  Know(Location(Obj), ObjLoc, ProbBefore) = true,
      IsRobot(RobObj) = true, Know(Location(RobObj), ObjLoc, 1) = true
```

Robot can examine his hand to see if it's empty or to see which object he is holding.
Theoretically, this does not require any preconditions. Practically, it does:

```   
ExamineHand(Obj, Arm, ProbBefore):
res:  Know(InHand(Arm), Obj, 1) = true
pre:  Know(InHand(Arm), Obj, ProbBefore) = true
```
