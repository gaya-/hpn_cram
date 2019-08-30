
from collections import OrderedDict # for World.location_poses

import hpncsp.miscUtil # for flatten()
import hpncsp.execute
import csplan.planner # for State
import csplan.constraints # for VarType, Constraint ...
import csplan.domain_globals # for WORLD


# # # # # # # # # # Environment # # # # # # # # # #


class WorldObject:
    possible_attributes = ('clean', 'dirty')

    def __init__(self, name, attributes, pose):
        """
        :param str name:
        :param list[str] attributes: has to be a list with elements in possible_attributes
        :param int pose:
        """
        self.name = name
        self.attributes = attributes
        self.pose = pose


class World(csplan.planner.State):
    location_poses = OrderedDict([('fridge', (0, 1, 2, 3)),
                                  ('stove', (4, 5, 6, 7)),
                                  ('sink', (8, 9, 10, 11)),
                                  ('table_1', (12, 13, 14, 15)),
                                  ('table_2', (16, 17, 18, 19))])
    world_length = len(hpncsp.miscUtil.flatten(location_poses.values()))
    possible_robot_hands = ['left', 'right']

    def __init__(self, objects, robot_base_pose,
                 object_in_left_hand = 'none', object_in_right_hand = 'none'):
        """
        :param list[WorldObject] objects:
        :param int robot_base_pose:
        :param str object_in_left_hand:
        :param str object_in_right_hand:
        """
        csplan.planner.State.__init__(self)
        self.objects = objects
        self.robot_base_pose = robot_base_pose
        self.objects_in_hands = {'left': object_in_left_hand, 'right': object_in_right_hand}

    def get_object_names(self):
        return [obj.name for obj in self.objects]

    def get_object_poses(self):
        return range(0, self.world_length)

    def get_robot_poses(self):
        return range(1, self.world_length - 1)

    def get_locations(self):
        return self.location_poses.keys()

    def get_robot_pose(self):
        return self.robot_base_pose

    def set_robot_pose(self, pose):
        self.robot_base_pose = pose

    def get_robot_hand_pose(self, hand):
        return self.get_robot_pose() + (1 if hand == 'right' else -1)

    def get_object_in_hand(self, hand):
        return self.objects_in_hands[hand]

    def set_object_in_hand(self, hand, name):
        self.objects_in_hands[hand] = name

    def get_object_with_name(self, name):
        object_as_list = [obj for obj in self.objects if obj.name == name]
        if object_as_list:
            return object_as_list[0]
        else:
            return None

    def get_object_pose(self, name):
        return self.get_object_with_name(name).pose

    def set_object_pose(self, name, pose):
        self.get_object_with_name(name).pose = pose

    def get_object_at_pose(self, pose):
        object_as_list = [obj for obj in self.objects if obj.pose == pose]
        if object_as_list:
            return object_as_list[0]
        else:
            return None

    def get_object_attributes(self, name):
        return self.get_object_with_name(name).attributes

    def add_object_attribute(self, name, new_attribute):
        self.get_object_with_name(name).attributes += [new_attribute]

    def remove_object_attribute(self, name, attribute):
        self.get_object_with_name(name).attributes.remove(attribute)

    def pose_at_location_p(self, pose, location):
        return pose in self.location_poses[location]

    def object_at_location_p(self, name, location):
        return self.pose_at_location_p(self.get_object_pose(name), location)

    def draw(self):
        # draw the air layer
        air_layer = ['  '] * self.world_length
        air_layer[self.get_robot_pose()] = 'RB'
        air_layer[self.get_robot_hand_pose('left')] = self.objects_in_hands['left'][0:2].upper()
        air_layer[self.get_robot_hand_pose('right')] = self.objects_in_hands['right'][0:2].upper()
        for i in air_layer:
            print '| ' + i,
        print '|'
        # draw the object layer
        object_layer = ['  '] * self.world_length
        for obj in self.objects:
            if obj.pose:
                object_layer[obj.pose] = obj.name[0:2].upper()
        for i in object_layer:
            print '| ' + i,
        print '|'
        for location in self.get_locations():
            print '|    ' + location + ' ' * (11 - len(location)) + '   ',
        print '|'

    def execute_prim(self, operator_name, params=None):
        if operator_name == 'go':
            # our robot is an aerial robot, so he can fly anywhere
            [start_pose, destination_pose] = params
            if start_pose == self.get_robot_pose() and destination_pose in self.get_robot_poses():
                self.set_robot_pose(destination_pose)
            else:
                raise Exception('Robot either was not at the expected pose or destination pose is out of bounds.')
        elif operator_name == 'pick':
            [name, hand, object_pose, robot_pose] = params
            if self.get_object_in_hand(hand) != 'none':
                raise Exception('Tried to pick with hand full')
            hand_pose = self.get_robot_hand_pose(hand)
            picked_object = self.get_object_at_pose(hand_pose)
            if picked_object is None:
                raise Exception('Tried to pick nothing')
            self.set_object_in_hand(hand, picked_object.name)
            self.set_object_pose(picked_object.name, None)
        elif operator_name == 'place':
            [name, hand, object_pose, robot_pose] = params
            if self.get_object_in_hand(hand) == 'none':
                raise Exception('Tried to place nothing')
            object_to_place_name = self.get_object_in_hand(hand)
            hand_pose = self.get_robot_hand_pose(hand)
            if self.get_object_at_pose(hand_pose) is not None:
                raise Exception('Tried to place in occupied location')
            self.set_object_in_hand(hand, 'none')
            self.set_object_pose(object_to_place_name, hand_pose)
        elif operator_name == 'wash':
            # Will wash any object in sink
            objects_at_sink = [self.get_object_at_pose(pose) for pose in self.location_poses['sink']]
            for obj in objects_at_sink:
                if obj is not None:
                    self.add_object_attribute(obj.name, 'clean')
        else:
            raise Exception, 'Unknown operator: ' + operator_name

    def check_signature(self):
        pass


# # # # # # # # # # Variable Types # # # # # # # # # #


class Obj(csplan.constraints.VarType): pass
class Hand(csplan.constraints.VarType): pass
class OPose(csplan.constraints.VarType): pass
class RPose(csplan.constraints.VarType): pass
class Loc(csplan.constraints.VarType): pass


# # # # # # # # # # Constraints # # # # # # # # # #


def generator_from_list(the_list):
    return iter(map(lambda x: [x], the_list))


######## TODO!!!! Fix the signature of TEST in Constraint, it never receives WORLD, default ASSIGNMENT shouldn't be None
class IsObj(csplan.constraints.Constraint):
    # used as IsObj[fork] = true/false

    types = [Obj]

    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        self.set_samplers([(self.object_sampler, [], False)])

    def object_sampler(self):
        return generator_from_list(csplan.domain_globals.WORLD.get_object_names())

    def test(self, assignment):
        [name] = self.get_values(assignment)
        return name in csplan.domain_globals.WORLD.get_object_names()


class IsHand(csplan.constraints.Constraint):
    # used as IsHand[left] = true/false

    types = [Hand]

    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        self.set_samplers([(self.hand_sampler, [], False)])

    def hand_sampler(self):
        return generator_from_list(csplan.domain_globals.WORLD.possible_robot_hands)

    def test(self, assignment):
        [hand] = self.get_values(assignment)
        return hand in csplan.domain_globals.WORLD.possible_robot_hands


class IsObjPose(csplan.constraints.Constraint):
    # used as IsObjPose[2] = true/false

    types = [OPose]

    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        self.set_samplers([(self.object_pose_sampler, [], False)])

    def object_pose_sampler(self):
        return generator_from_list(csplan.domain_globals.WORLD.get_object_poses())

    def test(self, assignment):
        [object_pose] = self.get_values(assignment)
        return object_pose in csplan.domain_globals.WORLD.get_object_poses()


class IsRobPose(csplan.constraints.Constraint):
    # used as IsRobPose[2] = true/false

    types = [RPose]

    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        self.set_samplers([(self.robot_pose_sampler, [], False)])

    def robot_pose_sampler(self):
        return generator_from_list(csplan.domain_globals.WORLD.get_robot_poses())

    def test(self, assignment):
        [robot_pose] = self.get_values(assignment)
        return robot_pose in csplan.domain_globals.WORLD.get_robot_poses()


class IsLoc(csplan.constraints.Constraint):
    # used as IsLoc[fridge] = true/false

    types = [Loc]

    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        self.set_samplers([(self.location_sampler, [], False)])

    def location_sampler(self):
        return generator_from_list(csplan.domain_globals.WORLD.get_locations())

    def test(self, assignment):
        [location] = self.get_values(assignment)
        return location in csplan.domain_globals.WORLD.get_locations()


class PoseInLocation(csplan.constraints.Constraint):
    # used as PoseInLocation[2, fridge] = true/false

    types = [OPose, Loc]

    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        # given the 1st argument aka the location, generate all the remaining ones aka the pose
        self.set_samplers([(self.pose_sampler, [1], False)])

    def pose_sampler(self, location):
        return generator_from_list(csplan.domain_globals.WORLD.location_poses[location])

    def test(self, assignment):
        [pose, location] = self.get_values(assignment)
        return pose in csplan.domain_globals.WORLD.location_poses[location]


class ExistsIK(csplan.constraints.Constraint):
    # used as ExistsIK[left, 0, 1] = true/false

    types = [Hand, OPose, RPose]

    ####TODO!!! how to decide which combinations to write samplers for
    def __init__(self, args):
        csplan.constraints.Constraint.__init__(self, args)
        # given the 0th and 2nd arguments aka hand and robot pose, generate all the remaining ones aka the object pose
        # given the 0th and 1st arguments, aka hand and object pose, generate all the remaining ones aka robot pose
        self.set_samplers([
            # (self.hand_sampler, [1, 2], True),
            (self.object_pose_sampler, [0, 2], True),
            (self.robot_pose_sampler, [0, 1], True)])

    def hand_sampler(self, object_pose, robot_pose):
        if object_pose == robot_pose + 1:
            yield ['right']
        elif object_pose == robot_pose - 1:
            yield ['left']
        return

    def object_pose_sampler(self, hand, robot_pose):
        object_pose = (robot_pose - 1) if (hand == 'left') else (robot_pose + 1)
        yield [object_pose]
        return

    def robot_pose_sampler(self, hand, object_pose):
        robot_pose = (object_pose + 1) if (hand == 'left') else (object_pose - 1)
        if robot_pose in csplan.domain_globals.WORLD.get_robot_poses():
            yield [robot_pose]
        return

    def test(self, assignment):
        [hand, object_pose, robot_pose] = self.get_values(assignment)
        hand_offset = -1 if hand == 'left' else +1
        return robot_pose + hand_offset == object_pose

    # Return None if these two constraints are inconsistent
    # Otherwise, return bindings.  If no bindings necessary, return {}
    # The reason for the bindings is that we might want to force some
    # variables to conform.
    ## TODO!!! what is this for?
    def is_consistent(self, other):
        if other.predicate != 'ExistsIK':
            return {}
        hand, object_pose, robot_pose = self.args
        other_hand, other_object_pose, other_robot_pose = other.args
        ## TODO!!!! check if this IF is really correct
        if (robot_pose == other_robot_pose and (hand == other_hand or object_pose == other_object_pose)) or \
                (hand == other_hand and object_pose == other_object_pose):
            # force everything to match
            return csplan.constraints.force_match(self.args, other.args)
        else:
            return {}


# # # # # # # # # # Fluents # # # # # # # # # #


class RobPose_C(csplan.constraints.FluentConstraint):
    # used as RobPose_C[] = 1

    def __init__(self, fluent, args, state):
        csplan.constraints.FluentConstraint.__init__(self, fluent, args, state)
        self.set_samplers([(self.robot_pose_sampler, [], True)])

    def robot_pose_sampler(self):
        yield [self.state.get_robot_pose()]


class RobPose(csplan.planner.Fluent):
    # used as RobPose[] = 1

    constraint_types = [RPose]
    constraint_class = RobPose_C

    def val_fun(self, args, state):
        return state.get_robot_pose()


class ObjPose_C(csplan.constraints.FluentConstraint):
    # used as ObjPose_C[milk] = 1

    def __init__(self, fluent, args, state):
        csplan.constraints.FluentConstraint.__init__(self, fluent, args, state)
        self.set_samplers([(self.object_pose_sampler, [0], True)])

    def object_pose_sampler(self, name):
        if name is not 'none':
            yield [self.state.get_object_pose(name)]


class ObjPose(csplan.planner.Fluent):
    # used as ObjPose[milk] = 1

    constraint_types = [Obj, OPose]
    constraint_class = ObjPose_C
    condition_on = True ### TODO!!!!!! what is this?

    def val_fun(self, args, state):
        [name] = args
        return state.get_object_pose(name) if name != 'none' else None


class InHand_C(csplan.constraints.FluentConstraint):
    # used as InHand_C[left] = milk

    def __init__(self, fluent, args, state):
        csplan.constraints.FluentConstraint.__init__(self, fluent, args, state)
        self.set_samplers([(self.object_sampler, [0], True),
                           (self.hand_sampler, [1], True)])

    def object_sampler(self, hand):
        yield [self.state.get_object_in_hand(hand)]
        return

    def hand_sampler(self, name):
        for hand in self.state.possible_robot_hands:
            if self.state.get_object_in_hand(hand) == name:
                yield [hand]
        return


class InHand(csplan.planner.Fluent):
    # used as InHand[left] = milk

    constraint_types = [Hand, Obj]
    constraint_class = InHand_C
    condition_on = True

    def val_fun(self, args, state):
        [hand] = args
        return state.get_object_in_hand(hand)


class Clear_C(csplan.constraints.FluentConstraint):
    # used as Clear_C[1] = true/false
    # says if a pose is clear of objects

    def __init__(self, fluent, args, state):
        csplan.constraints.FluentConstraint.__init__(self, fluent, args, state)
        self.set_samplers([(self.pose_sampler, [], False)])

    def pose_sampler(self):
        return generator_from_list([pose for pose in self.state.get_object_poses()
                                    if self.state.get_object_at_pose(pose) is None])


class Clear(csplan.planner.Fluent):
    # used as Clear[1] = true/false

    constraint_types = [OPose]
    constraint_class = Clear_C

    def val_fun(self, args, state):
        [object_pose] = args
        return state.get_object_at_pose(object_pose) == None


class ObjLoc(csplan.planner.Fluent):
    # used as ObjLoc[milk, fridge] = true/false

    constraint_types = [Obj, Loc]

    def val_fun(self, args, state):
        [name, location] = args
        return state.object_at_location_p(name, location)


class Clean(csplan.planner.Fluent):
    # used as Clean[plate] = true/false

    constraint_types = [Obj]

    def val_fun(self, args, state):
        [name] = args
        return 'clean' in state.get_object_attributes(name)


class Dirty(csplan.planner.Fluent):
    # used as Dirty[plate] = true/false

    constraint_types = [Obj]

    def test(self, state):
        [name] = self.args
        return 'clean' not in state.get_object_attributes(name)


# # # # # # # # # # Operators # # # # # # # # # #

# Primitives

def go_prim(state, env, args):
    env.execute_prim('go', args)

def pick_prim(state, env, args):
    env.execute_prim('pick', args)

def place_prim(state, env, args):
    env.execute_prim('place', args)

def wash_prim(state, env, args):
    env.execute_prim('wash', args)

# VarType variable name to type mappings

def var_name_to_type(variable_name):
    mapping = {'RPo': RPose,
               'OPo': OPose,
               'Han': Hand,
               'Obj': Obj,
               'Loc': Loc}
    return mapping[variable_name[:3]]

csplan.domain_globals.type_constructors = var_name_to_type

# Operators

go = csplan.planner.Operator(
    name='go',
    skel_args=[],
    args=['RPose1', 'RPose2'],
    preconditions=[
        RobPose([], 'RPose1')],
    constraints={
        IsRobPose(['RPose1']),
        IsRobPose(['RPose2'])},
    results=[
        RobPose([], 'RPose2')],
    prim_fn=go_prim)

pick = csplan.planner.Operator(
    name='pick',
    skel_args=[],
    args=['Obj', 'Hand', 'OPose', 'RPose'],
    preconditions=[
        InHand(['Hand'], 'none'),
        ObjPose(['Obj'], 'OPose'),
        RobPose([], 'RPose')],
    constraints={
        ExistsIK(['Hand', 'OPose', 'RPose']),
        IsObj(['Obj']),
        IsHand(['Hand']),
        IsObjPose(['OPose']),
        IsRobPose(['RPose'])},
    results=[
        InHand(['Hand'], 'Obj'),
        Clear(['OPose'], True)],
    prim_fn=pick_prim)

place = csplan.planner.Operator(
    name='place',
    skel_args=[],
    args=['Obj', 'Hand', 'OPose', 'RPose'],
    preconditions=[
        InHand(['Hand'], 'Obj'),
        RobPose([], 'RPose'),
        Clear(['OPose'], True)],
    constraints={
        ExistsIK(['Hand', 'OPose', 'RPose']),
        IsObj(['Obj']),
        IsHand(['Hand']),
        IsObjPose(['OPose']),
        IsRobPose(['RPose'])},
    results=[
        ObjPose(['Obj'], 'OPose'),
        InHand(['Hand'], 'none'),
        Clear(['OPose'], False)],
    prim_fn=place_prim)

place_at_loc = csplan.planner.Operator(
    name='place_at_loc',
    skel_args=[],
    args=['Obj', 'Loc', 'OPose'],
    preconditions=[
        ObjPose(['Obj'], 'OPose')],
    constraints={
        PoseInLocation(['OPose', 'Loc']),
        IsObj(['Obj']),
        IsLoc(['Loc']),
        IsObjPose(['OPose'])},
    results=[
        ObjLoc(['Obj', 'Loc'], True)
    ])

wash = csplan.planner.Operator(
    name='wash',
    skel_args=[],
    args=['Obj'],
    preconditions=[
        ObjLoc(['Obj', 'sink'], True)],
    constraints={
        IsObj(['Obj'])},
    results=[
        Clean(['Obj'], True)],
    prim_fn=wash_prim)


# # # # # # # # # # Planner Function # # # # # # # # # #


def planner(file_suffix):
    def p(state, goal, plan_stack, flat_plan):
        plan = csplan.planner.plan_backward(
            state, goal,
            {'go': go, 'pick': pick, 'place': place, 'place_at_loc': place_at_loc, 'wash': wash},
            plan_stack, flat_plan=flat_plan, file_tag=file_suffix, useH=True, use_helpful_actions=True)
        return plan
    return p


# # # # # # # # # # Tests # # # # # # # # # #


def test():
    hpncsp.globals.glob.heuristic_split_aggressively = False
    hpncsp.globals.glob.use_helpful_actions = True
    hpncsp.globals.glob.outDir = '/home/gaya/workspace/python/hpn_cram/toy_hpncsp/'
    csplan.planner.CONSTRAINT_SOLVER = 'backtrack'

    milk = WorldObject('milk_1', [], 1)
    plate = WorldObject('plate_1', ['dirty'], 9)
    cup = WorldObject('cup_1', ['dirty'], 19)
    fork = WorldObject('fork_1', ['clean'], 13)
    world = World(objects=[milk, plate, cup, fork], robot_base_pose=6)

    csplan.domain_globals.WORLD = world

    initial_state = world

    goals = [csplan.planner.Goal([RobPose([], 5)], []),
             csplan.planner.Goal([InHand(['left'], 'milk_1')], []),
             csplan.planner.Goal([ObjPose(['milk_1'], 12)], []),
             csplan.planner.Goal([ObjLoc(['milk_1', 'sink'], True)], []),
             csplan.planner.Goal([Clean(['cup_1'], True)], [])] # <- goals[4] too big search tree

    hpncsp.execute.HPN(initial_state, goals[3], world, planner('_t1'))

    world.draw()

test()