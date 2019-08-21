
import hpn.fbch  # for Fluent

from toy_fetch_place.world import *
from toy_fetch_place.world_state import *


class RobotName(hpn.fbch.Fluent):
    predicate = 'RobotName'

    def test(self, world_state):
        """
        Say if the argument is a valid robot name
        Robot() = RobotName
        :param world_state:
        :return str:
        """
        return world_state.get_robot_name()


class Location(hpn.fbch.Fluent):
    predicate = 'Location'

    def test(self, world_state):
        """
        Location(ItemName) = LocationName
        TODO: !!!!!!!!!!!!!!!!!!!!! figure out how to deal with objects that can be in both hands, so multiple locations
        :param World world_state:
        :return str:
        """
        [item_name] = self.args
        locations = world_state.get_item_locations(item_name)
        if locations:
            return locations[0]
        else:
            raise Exception("The item {} did not have a location! O_O".format(item_name))


class InHand(hpn.fbch.Fluent):
    predicate = 'InHand'

    def test(self, world_state):
        """
        InHand(HandName) = ItemName
        :param world_state:
        :return str | None:
        """
        [hand] = self.args
        items_in_hand = world_state.get_items_at_location(hand)
        if items_in_hand:
            return items_in_hand[0].name
        else:
            return None

    # def fglb(self, other_fluent, world_state):
    #     """
    #     Makes sure that the planner knows that a robot cannot two objects in the hand at the same time,
    #     or that the robot cannot have None and an object in the hand at the same time.
    #     :param other_fluent:
    #     :param world_state:
    #     :return:
    #     """
    #     [hand] = self.args
    #     if other_fluent.predicate == 'InHand':
    #         [other_hand] = other_fluent.args
    #         # one hand cannot have two objects at the same time
    #         if hand == other_hand and self.value != other_fluent.value:
    #             # Copied from LPK: Basic FBCH already does this case, but I think since we're
    #             # overriding this method now, we have to handle it.
    #             return False, {}
    #         # An object actually can be in two hands during dual-arm grasp
    #         # elif hand != other_hand and self.value == other_fluent.value:
    #         #     return False, {}
    #         else:
    #             return {self, other_fluent}, {}
    #     else:
    #         return {self, other_fluent}, {}


class ContainerState(hpn.fbch.Fluent):
    predicate = "ContainerState"

    def test(self, world_state):
        """
        ContainerState(ContainerName) = open/closed
        :param WorldState world_state:
        :return str:
        """
        [container_name] = self.args
        result =  world_state.environment.get_container_state(container_name)
        return result