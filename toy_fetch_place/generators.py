
import hpn.fbch  # for Function
import hpnutil.miscUtil  # for isVar

from toy_fetch_place.world import *
from toy_fetch_place.world_state import *


class GenRobotName(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        yield [world_state.get_robot_name()]
        return


class GenGoStartLocation(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Returns a location where the robot might have been when he wanted to go to a destination location.
        Going to only return current robot location, at that also only if the location is != destination.
        Not going to consider any other possible locations, because the inflate the search tree....
        :param generator_args:
        :param goal_fluents:
        :param WorldState world_state:
        :return:
        """
        [destination_location] = generator_args
        current_robot_location = world_state.get_item_locations(world_state.get_robot_name())[0]
        if destination_location == current_robot_location:
            return
        else:
            return [[current_robot_location]]


class GenPickUpItemLocation(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Returns a location where the robot should go such that it can pick up an item.
        :param generator_args:
        :param goal_fluents:
        :param WorldState world_state:
        :return:
        """
        [item_name] = generator_args
        # the item_name has to be bound
        if hpnutil.miscUtil.isVar(item_name) or item_name == None:
            return
        item_with_given_name = world_state.get_item_with_name(item_name)
        current_item_locations = world_state.get_item_locations(item_name)
        current_location_without_in_hand = set(current_item_locations).difference(set(world_state.robot.possible_arms))
        # by now, current_location_without_in_hand has to be only one value or no value
        if current_location_without_in_hand:
            current_location_without_in_hand = current_location_without_in_hand.pop()
            yield [current_location_without_in_hand]
        return
        ### returning all other solutions makes the search tree huge.
        ### so we're only going to return the actual location of the object and that's it...
        # # if the current location of item didn't work, means the item has been moved in the meanwhile,
        # # so just return all other values
        # remaining_locations = set(world_state.environment.possible_locations)
        # if current_location_without_in_hand:
        #     remaining_locations.remove(current_location_without_in_hand)
        # for location in remaining_locations:
        #     yield [location]
        # return


class GenRegraspNewArm(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Suggests an arm to regrasp into for freeing up an arm. Has to be an arm that is free at the moment.
        :param generator_args:
        :param goal_fluents:
        :param world_state:
        :return:
        """
        [arm_holding_an_object] = generator_args
        item_in_the_arm = world_state.robot.get_item_in_hand(arm_holding_an_object)
        # if the robot is not holding anything in the hand right now, it is impossible to regrasp that None object
        # TODO: deal with this problem in a better way
        if not item_in_the_arm:
            return
        all_arms = world_state.robot.possible_arms
        all_free_arms = [arm for arm in all_arms if not world_state.robot.get_item_in_hand(arm)]
        # first try all free arms
        for currently_free_arm in all_free_arms:
            yield [currently_free_arm, item_in_the_arm.name]
        # if that doesn't help, try busy arms, but make sure you're not regrasping from A to A
        non_free_arms = set(all_arms).difference(set(all_free_arms)).difference(set([arm_holding_an_object]))
        for currently_non_free_arm in non_free_arms:
            yield [currently_non_free_arm, item_in_the_arm.name]
        return


class GenRegraspCurrentArm(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Suggests an arm to regrasp from for freeing up an arm. Has to be an arm that is holding the object.
        :param generator_args:
        :param goal_fluents:
        :param world_state:
        :return:
        """
        [arm_to_regrasp_into, item_name] = generator_args
        arms_holding_the_object = world_state.robot.get_hands_holding_item(item_name)
        for arm_holding_the_object in arms_holding_the_object:
            if arm_holding_the_object != arm_to_regrasp_into:
                yield [arm_holding_the_object]
        return


# class GenPlaceItemNameAndLocation(hpn.fbch.Function):
#     @staticmethod
#     def fun(generator_args, goal_fluents, world_state):
#         """
#         Given an arm to free by placing an object, what should be the item and the location to place the item?
#         Answer: the item should be the one we're holding and the location should be robot's location.
#         :param generator_args:
#         :param goal_fluents:
#         :param world_state:
#         :return:
#         """
#         [arm_to_free, robot_name] = generator_args
#         item_in_the_arm = world_state.robot.get_item_in_hand(arm_to_free)
#         robot_location = world_state.get_item_locations(robot_name)[0]
#         if item_in_the_arm:
#             yield [item_in_the_arm.name, robot_location]
#         return


class GenPlaceLocation(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """Just gives the current robot location back"""
        yield world_state.get_item_locations(world_state.get_robot_name()) # it's already a vector
        return


class GenPlaceArm(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Given an item_name, what should be the arm to place the item_name?
        Answer: the arm that is currently holding the object.
        If the arm is not holding an object right now, it might some time later, so give all arms. Prefer free ones.
        :param generator_args:
        :param goal_fluents:
        :param world_state:
        :return:
        """
        [item_name] = generator_args
        arms_holding_item = world_state.robot.get_hands_holding_item(item_name)
        for arm in arms_holding_item:
            yield [arm]
        all_arms = world_state.robot.possible_arms
        all_free_arms = [arm for arm in all_arms if not world_state.robot.get_item_in_hand(arm)]
        all_free_arms = set(all_free_arms).difference(set(arms_holding_item))
        # first try all free arms
        for currently_free_arm in all_free_arms:
            yield [currently_free_arm]
        # if that doesn't help, try busy arms, but make sure you're not regrasping from A to A
        non_free_arms = set(all_arms).difference(set(all_free_arms))
        for currently_non_free_arm in non_free_arms:
            yield [currently_non_free_arm]
        return


class GenPlaceItemName(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """Suggests an item name to place down, given the arm. Prefers the item the robot is holding at the moment."""
        [arm] = generator_args
        all_item_names = [item.name for item in world_state.items]
        all_item_names = set(all_item_names).difference({world_state.get_robot_name()})
        item_in_hand = world_state.robot.get_item_in_hand(arm)
        if item_in_hand:
            yield [item_in_hand.name]
            all_item_names = all_item_names.difference({item_in_hand.name})
        for it_name in all_item_names:
            yield [it_name]


class GenFreeArm(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Suggest an arm to open a container with. Or perform any other manipulation action that needs a free hand.
        Prefer currently free arms.
        :param generator_args:
        :param goal_fluents:
        :param world_state:
        :return:
        """
        all_arms = world_state.robot.possible_arms
        all_free_arms = [arm for arm in all_arms if not world_state.robot.get_item_in_hand(arm)]
        # first try all free arms
        for currently_free_arm in all_free_arms:
            yield [currently_free_arm]
        # if that doesn't help, try busy arms
        non_free_arms = set(all_arms).difference(set(all_free_arms))
        for currently_non_free_arm in non_free_arms:
            yield [currently_non_free_arm]
        return


class GenCurrentContainerState(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """
        Suggests a container state given a container name. Prefers the current state.
        :param generator_args:
        :param goal_fluents:
        :param world_state:
        :return:
        """
        [container_name] = generator_args
        current_state = world_state.environment.get_container_state(container_name)
        yield [current_state]
        for state in set(world_state.environment.possible_container_states).difference({current_state}):
            yield [state]
        return


class GenExamineRegressProb(hpn.fbch.Function):
    @staticmethod
    def fun(generator_args, goal_fluents, world_state):
        """Suggests a probability prior to examine operation.
        As that probability doesn't matter, we should return all probability values."""
        for i in [0.5, 0.75, 0.25, 1, 0]:
            yield [i]
        return