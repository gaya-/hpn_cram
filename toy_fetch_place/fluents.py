
import hpn.fbch  # for Fluent
import hpn.belief  # for Know fluent, which is a nested belief fluent
import hpnutil.miscUtil  # for isVar in Know fluent

from toy_fetch_place.world import *
from toy_fetch_place.world_state import *


class ConfidenceFluent(hpn.fbch.Fluent):
    def probability(self, world_state):
        '''
        This function should return a number between 0 and 1,
        which should represent the probability that the fluent holds,
        i.e. the confidence of the fluent in the value that test() returns.
        Should be implemented by any fluent that can be passed to the Know fluent as an argument
        :param WorldState world_state:
        :return float: probability number real between 0 and 1
        '''
        raise NotImplementedError


class Know(hpn.belief.BFluent):
    predicate = 'Know'
    # Parameters are nested_fluent, value, probability/confidence
    # This class is based on (copy pasted and adapted from) hpn.belief.Bd

    def update(self):
        if not hpnutil.miscUtil.isVar(self.args[0]):
            # Set the value in the embedded fluent
            self.args[0].value = self.args[1]
            # Clear out strings, keep house
            self.args[0].update()
        super(self.__class__, self).update()

    # Try to make this hash well, but also be optimistic.  In this case, p down
    def optArgString(self):
        if hpnutil.miscUtil.isVar(self.args[2]):
            probStr = self.args[2]
        else:
            probStr = str(hpnutil.miscUtil.roundDownStr(self.args[2], 2))
        return '['+ self.args[0].prettyString(False, includeValue = False) + \
               ', ' + hpn.fbch.prettyString(self.args[1], False) + ',' + probStr + ']'

    # def getValueGrounding(self, bstate):
    #     (rFluent, v, p) = self.args
    #     if not isGround(rFluent.args):
    #         return {}
    #     dv = rFluent.dist(bstate.details)
    #     b = {}
    #     if isAnyVar(v):
    #         b[v] = dv.mode()
    #     if isAnyVar(p):
    #         b[p] = dv.prob(dv.mode())
    #     return b

    def getArgGrounding(self, state, extras = None):
        (nested_fluent, value, probability) = self.args
        # See if we have a domain-dependent way to do this
        return nested_fluent.getArgGrounding(state, (value, probability))

    # True if the "nested_fluent" has value "value" with probability greater than "probability"
    def test(self, world_state):
        (nested_fluent, value, probability) = self.args
        assert hpnutil.miscUtil.isVar(probability) or (0 <= probability <= 1) or probability == None
        fluent_value = nested_fluent.test(world_state)
        fluent_probability = nested_fluent.probability(world_state)
        return fluent_value == value and fluent_probability >= probability


class IsRobot(hpn.fbch.Fluent):
    predicate = 'IsRobot'

    def test(self, world_state):
        """
        Say if the argument is a valid robot name
        IsRobot(RobotName) = true/false
        :param world_state:
        :return str:
        """
        [robot_name] = self.args
        return robot_name == world_state.get_robot_name()


class Location(ConfidenceFluent):
    predicate = 'Location'

    def test(self, world_state):
        """
        Location(ItemName) = LocationName
        TODO: figure out how to deal with objects that can be in both hands, so multiple locations
        :param World world_state:
        :return str:
        """
        [item_name] = self.args
        locations = world_state.get_item_locations(item_name)
        if locations:
            return locations[0]
        else:
            raise Exception("The item {} did not have a location! O_O".format(item_name))

    def probability(self, world_state):
        [item_name] = self.args
        item_location = self.test(world_state)
        return world_state.get_probability_of_item_at_location(item_name, item_location)


class InHand(ConfidenceFluent):
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

    def probability(self, world_state):
        [hand] = self.args
        name_of_item_in_hand = self.test(world_state)
        if name_of_item_in_hand:
            return world_state.get_probability_of_item_in_hand(name_of_item_in_hand, hand)
        else:
            return 0.5


class ContainerState(ConfidenceFluent):
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

    def probability(self, world_state):
        [container_name] = self.args
        container_state = self.test(world_state)
        return world_state.get_probability_of_container_state(container_name, container_state)
