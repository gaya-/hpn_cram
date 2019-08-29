
import copy  # for creating world state equivalents for real-world objects

from toy_fetch_place.world import Item, Robot, Environment, World


class WorldStateItem(Item):
    def __init__(self, name, item_type):
        Item.__init__(self, name, item_type)

    @classmethod
    def to_world_state(cls, item):
        world_state_item = WorldStateItem(item.name, item.item_type)
        return world_state_item


class WorldStateRobot(Robot):
    def __init__(self, name, items_in_hands=None):
        Robot.__init__(self, name, items_in_hands)
        # Maps hand to confidence that I have the specific object in that hand
        # Question: am I as confident about my beliefs of having objects in hands as not having anything in the hand?
        # Things don't suddenly appear in my hand, but they do suddenly disappear -.- robot life...
        self.items_in_hands_confidences = {arm: 0.5 for arm in self.items_in_hands.keys()}

    @classmethod
    def to_world_state(cls, robot):
        items_in_hands_copy = {}
        for (hand, item) in robot.items_in_hands.items():
            items_in_hands_copy[hand] = WorldStateItem.to_world_state(item) if item else None
        world_state_robot = cls(robot.name, items_in_hands_copy)
        return world_state_robot

    def get_item_in_hand_confidence(self, hand):
        return self.items_in_hands_confidences[hand]

    def set_item_in_hand_confidence(self, hand, confidence):
        self.items_in_hands_confidences[hand] = confidence


class WorldStateEnvironment(Environment):
    def __init__(self, name, items_at_locations=None, container_states=None):
        Environment.__init__(self, name, items_at_locations, container_states)
        self.container_states_confidences = {location: 0.5 for location in self.container_states.keys()}
        self.items_at_locations_confidences = {}
        for (location, items_list) in self.items_at_locations.items():
            self.items_at_locations_confidences[location] = {item_name: 0.5 for item_name in items_list}

    @classmethod
    def to_world_state(cls, environment):
        items_at_locations_copy = {}
        for (location, items_list) in environment.items_at_locations.items():
            items_at_locations_copy[location] = map(lambda item: WorldStateItem.to_world_state(item), items_list)
        container_states_copy = copy.copy(environment.container_states)
        world_state_environment = cls(environment.name, items_at_locations_copy, container_states_copy)
        return world_state_environment

    def get_location_state_confidence(self, container):
        # return self.container_states_confidences[container] if container in self.container_locations else 1.0
        # decided that because there's no way to perceive a container state atm, we should just have 1.0 confidence
        return 1.0

    def get_item_at_location_confidence(self, location, item_name):
        if item_name in self.items_at_locations_confidences[location].keys():
            return self.items_at_locations_confidences[location][item_name]
        else:
            return 0.5

    def set_item_at_location_confidence(self, item_location, item_name, confidence):
        if confidence == 0:
            self.items_at_locations_confidences[item_location].pop(item_name, None)
        else:
            self.items_at_locations_confidences[item_location][item_name] = confidence





class WorldState(World):
    def __init__(self, environment, robot, operator_fail_probabilities):
        World.__init__(self, environment, robot, operator_fail_probabilities)
        # set the confidence in robot location to 1, assume the localization is really good
        robot_name = self.get_robot_name()
        robot_location = self.get_item_locations(robot_name)[0]
        self.environment.set_item_at_location_confidence(robot_location, robot_name, 1)

    @classmethod
    def to_world_state(cls, world):
        world_state = cls(WorldStateEnvironment.to_world_state(world.environment),
                          WorldStateRobot.to_world_state(world.robot),
                          copy.copy(world.operator_fail_probabilities))
        return world_state

    def draw(self):
        chars_in_left_column = 40
        print 'ROBOT {}:'.format(self.robot.name)
        for arm in self.robot.possible_arms:
            left_column_entry = '   {}: '.format(arm)
            print left_column_entry + ' ' * (chars_in_left_column - len(left_column_entry)),
            item_in_hand = self.robot.get_item_in_hand(arm)
            print (item_in_hand.name if item_in_hand else 'None'),
            print '({})'.format(self.robot.get_item_in_hand_confidence(arm))
        print
        print 'ENVIRONMENT {}:'.format(self.environment.name)
        for location in self.environment.possible_locations:
            left_column_entry = '   {}({}): '.format(location, self.environment.get_container_state(location))
            print left_column_entry + ' ' * (chars_in_left_column - len(left_column_entry)),
            for item in self.environment.get_items_at_location(location):
                print item.name + ' ({})'.format(self.environment.get_item_at_location_confidence(location, item.name))\
                      + '  ',
            print
        print

    def get_probability_of_item_in_hand(self, item_name, hand):
        """
        :param str item_name:
        :param str hand:
        :return float: returns the probability that the item is indeed in the hand
        """
        # TODO: for now ignoring item_name, but should actually compare with the belief state maybe?
        # if self.get_item_in_hand[hand] == item_name
        return self.robot.get_item_in_hand_confidence(hand)

    def get_probability_of_container_state(self, container_name, container_state):
        """
        :param str container_name:
        :param str container_state:
        :return float: returns the probability that the item is indeed in the given state
        """
        return self.environment.get_location_state_confidence(container_name)

    def get_probability_of_item_at_location(self, item_name, item_location):
        if item_location in self.environment.possible_locations:
            return self.environment.get_item_at_location_confidence(item_location, item_name)
        elif item_location in self.robot.possible_arms:
            return self.get_probability_of_item_in_hand(item_name, item_location)

    def set_probability_of_item_at_location(self, item_name, old_location, new_location, confidence):
        # remove old confidence
        if old_location in self.environment.possible_locations:
            self.environment.set_item_at_location_confidence(old_location, item_name, 0)
        elif old_location in self.robot.possible_arms:
            self.robot.set_item_in_hand_confidence(old_location, 0.5)
        # add new confidence
        if new_location in self.environment.possible_locations:
            self.environment.set_item_at_location_confidence(new_location, item_name, confidence)
        elif new_location in self.robot.possible_arms:
            self.robot.set_item_in_hand_confidence(new_location, confidence)