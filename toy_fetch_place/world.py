
class Item:
    possible_types = ('spoon', 'fork', 'cup', 'bowl', 'plate', 'milk', 'cereal', 'robot')

    def __init__(self, name, item_type):
        """
        :param str name: item unique name
        :param str item_type: one of the self.possible_types
        """
        self.name = name
        if item_type not in self.possible_types:
            raise Exception('Object type can only be one of following strings: {}'.format(self.possible_types))
        self.item_type = item_type


class Robot(Item):
    possible_arms = ('left_arm', 'right_arm')

    def __init__(self, name, items_in_hands=None):
        """
        :param str name: robot's name
        :param dict[str, Item | None] items_in_hands: the items the robot is holding in the hands
        """
        Item.__init__(self, name, 'robot')
        if items_in_hands and set(items_in_hands.keys()).difference(set(self.possible_arms)):
            raise Exception('items_in_hands can only have hands as one of following strings: {}'.
                            format(self.possible_arms))
        self.items_in_hands = {arm: None for arm in self.possible_arms}
        if items_in_hands:
            for (hand, item) in items_in_hands.items():
                if item and item.item_type == 'robot':
                    raise Exception('Robot cannot be holding a robot in his hands: {}'.format(item.name))
                self.items_in_hands[hand] = item

    def get_item_in_hand(self, hand):
        """
        :param str hand: one of the self.possible_arms
        :return Item | None: the item the robot is holding in that hand
        """
        return self.items_in_hands[hand] if hand in self.possible_arms else None

    def get_all_items(self):
        return [self.get_item_in_hand(arm) for arm in self.possible_arms if self.get_item_in_hand(arm)]

    def get_hands_holding_item(self, item_name):
        """
        :param str item_name: the name of the item we're looking for
        :return str: the hand or hands (one of self.possible_arms) which is/are holding the item, otherwise None
        """
        return [hand for (hand, item) in self.items_in_hands.items() if item and item.name == item_name]

    def set_item_in_hand(self, item, hand):
        """
        :param str hand:
        :param Item item:
        """
        if hand not in self.possible_arms:
            raise Exception('hand can only be one of {}.'.format(self.possible_arms))
        if self.items_in_hands[hand]:
            raise Exception('robot already holding item {} in {} hand.'.format(self.items_in_hands[hand].name, hand))
        if item.item_type == 'robot':
            raise Exception('Robot cannot hold another robot or himself: {}.'.format(item.name))
        self.items_in_hands[hand] = item

    def remove_item_from_hand(self, item, hand):
        """
        :param str hand:
        :param Item item:
        """
        if hand not in self.possible_arms:
            raise Exception('hand can only be one of {}.'.format(self.possible_arms))
        hands_holding_object = self.get_hands_holding_item(item.name)
        if not hands_holding_object or hand not in hands_holding_object:
            raise Exception("item {} is not in robot's {}.".format(item.name, hand))
        # only one object can be held per hand, so if we remove the object, we're left with None
        self.items_in_hands[hand] = None


class Environment:
    possible_locations = ('fridge', 'sink_drawer_lower', 'sink_drawer_middle', 'sink_drawer_upper',
                          'oven_vertical_drawer_right',
                          'sink_area_counter_top', 'kitchen_island_counter_top',
                          'floor')
    container_locations = possible_locations[0:5]
    possible_container_states = ('open', 'closed')

    def __init__(self, name, items_at_locations=None, container_states=None):
        """
        :param str name: the name of the environment
        :param dict[str, list(Item)] items_at_locations: maps a location to a list of items located at it,
                                                         whereby a location has to be one of self.possible_locations
        :param dict[str, str] container_states: {'container': 'state'}, where state is either 'open' or 'closed'
        """
        self.name = name
        if items_at_locations and set(items_at_locations.keys()).difference(set(self.possible_locations)):
            raise Exception('items_at_locations can only have locations as one of following strings: {}'.
                            format(self.items_at_locations))
        self.items_at_locations = {location: [] for location in self.possible_locations}
        if items_at_locations:
            for (location, items) in items_at_locations.items():
                self.items_at_locations[location] = items
        if container_states and (set(container_states.keys()).difference(set(self.container_locations)) or
                                 set(container_states.values()).difference(set(self.possible_container_states))):
            raise Exception('container_states can only have keys as one of {} and values as one of {}'.
                            format(self.container_locations, self.possible_container_states))
        self.container_states = {location: 'closed' for location in self.container_locations}
        if container_states:
            for (container, state) in container_states.items():
                self.container_states[container] = state

    def get_container_state(self, container):
        return self.container_states[container] if container in self.container_locations else 'open'

    def set_container_state(self, state, container):
        """
        :param str container: the name of the container to open or close, one of self.container_locations
        :param str state: either 'open' or 'closed'
        """
        if state not in self.possible_container_states:
            raise Exception('container state can only be one of {}'.format(self.possible_container_states))
        self.container_states[container] = state

    def get_items_at_location(self, location):
        if location in self.possible_locations:
            return self.items_at_locations[location]
        else:
            return None

    def get_all_items(self):
        all_items = []
        for location in self.possible_locations:
            if self.get_items_at_location(location):
                all_items.extend(self.get_items_at_location(location))
        return all_items

    def get_location_of_item(self, item_name):
        location_as_list = [location for location, items in self.items_at_locations.items()
                            if [item for item in items if item.name == item_name]]
        return location_as_list[0] if location_as_list else None

    def remove_item_from_location(self, item, location):
        current_location = self.get_location_of_item(item.name)
        # check if object is indeed at the start location
        # if object_with_given_name.location != start_location:
        #     raise Exception('The object to move is not at the expected start location.')
        # check if the location is the same as the old location
        if location != current_location:
            raise Exception('item {} is located at {} and not at {}'.format(item.name, current_location, location))
        if location in self.container_locations and self.get_container_state(location) != 'open':
            raise Exception('cannot take item {} out of {} because it is unaccessible.'.format(item.name, location))
        self.items_at_locations[location] = [it for it in self.items_at_locations[location] if it.name != item.name]

    def add_item_at_location(self, item, location):
        if location in self.container_locations and self.get_container_state(location) != 'open':
            raise Exception('cannot add item {} at {} because it is unaccessible.'.format(item.name, location))
        self.items_at_locations[location].append(item)


class World:
    def __init__(self, environment, robot, operator_fail_probabilities):
        """
        :param Environment environment:
        :param Robot robot:
        :param dict[str: float] operator_fail_probabilities: maps operator names to probabilities,
                                                             where a probability is between [0; 1]
        """
        self.environment = environment
        self.robot = robot
        # check that the items list doesn't contain any redundant item names
        items = environment.get_all_items() + robot.get_all_items()
        items_names = map(lambda lambda_items: lambda_items.name, items)
        if len(set(items_names)) < len(items_names):
            raise Exception('World cannot have two items with the same name: {}'.format(items_names))
        # check that all items have been assigned to a location
        for item in items:
            if not self.get_item_locations(item.name):
                raise Exception('All items should have a location in the robot hand or environment. {} does not'.
                                format(item.name))
        self.items = items
        self.operator_fail_probabilities = operator_fail_probabilities

    def draw(self):
        chars_in_left_column = 40
        print 'ROBOT {}:'.format(self.robot.name)
        for arm in self.robot.possible_arms:
            left_column_entry = '   {}: '.format(arm)
            print left_column_entry + ' ' * (chars_in_left_column - len(left_column_entry)),
            item_in_hand = self.robot.get_item_in_hand(arm)
            print item_in_hand.name if item_in_hand else ''
        print
        print 'ENVIRONMENT {}:'.format(self.environment.name)
        for location in self.environment.possible_locations:
            left_column_entry = '   {}({}): '.format(location, self.environment.get_container_state(location))
            print left_column_entry + ' ' * (chars_in_left_column - len(left_column_entry)),
            for item in self.environment.get_items_at_location(location):
                print item.name + '  ',
            print
        print

    def get_item_with_name(self, name):
        """
        :param str name: name of the item we're looking for in the world
        :return Item: either an Item or an error if there isn't an item with that name in the world
        """
        item_as_list = [item for item in self.items if item.name == name]
        if item_as_list:
            return item_as_list[0]
        else:
            raise Exception('There was no item {} in the world.'.format(name))

    def get_items_at_location(self, location):
        """
        :param str location: one of the possible locations of the environment or robot hands
        :return list[Item] | None: items located at location
        """
        if self.robot.get_item_in_hand(location):
            return [self.robot.get_item_in_hand(location)]
        else:
            return self.environment.get_items_at_location(location)

    def get_item_locations(self, item_name):
        return [self.environment.get_location_of_item(item_name)] or self.robot.get_hands_holding_item(item_name)

    def remove_item_at_location(self, item_name, location):
        item = self.get_item_with_name(item_name)
        if self.environment.get_location_of_item(item_name):
            # item is in the environment
            self.environment.remove_item_from_location(item, location)
        elif self.robot.get_hands_holding_item(item_name):
            # item is in robot's hand
            self.robot.remove_item_from_hand(item, location)
        else:
            raise Exception("invalid location {}".format(location))

    def add_item_at_location(self, item_name, location):
        item = self.get_item_with_name(item_name)
        if item.item_type == 'robot' and location in self.robot.possible_arms:
            raise Exception("Cannot move robot into its hand {}".format(location))
        if location in self.environment.possible_locations:
            self.environment.add_item_at_location(item, location)
        elif location in self.robot.possible_arms:
            self.robot.set_item_in_hand(item, location)
        else:
            raise Exception("invalid location {}".format(location))

    def move_item_or_robot(self, item_name, start_location, goal_location):
        """
        :param str item_name: name of the item we want to take into the hand
        :param str start_location: current location from which we want to take the item
        :param str goal_location: goal location where we want to place the item
        """
        # check if item is indeed at the assumed start_location
        if not self.get_items_at_location(start_location) or\
                item_name not in map(lambda lambda_item: lambda_item.name, self.get_items_at_location(start_location)):
            raise Exception('Item {} is not at the expected location {}.'.format(item_name, start_location))
        # check if the goal location is the same as current location
        if start_location == goal_location:
            return
        # if we are not moving the robot but an item,
        if self.get_item_with_name(item_name).item_type != 'robot':
            # first, the items can only move into or from robot hand,
            if start_location not in self.robot.possible_arms and goal_location not in self.robot.possible_arms:
                raise Exception('Items can only be moved into or from a robot hand: {} from {} to {}.'.
                                format(item_name, start_location, goal_location))
            # second, unless it's a regrasp with another arm operation,
            # the robot can manipulate an object only if he's at the same location as the object
            elif not(start_location in self.robot.possible_arms and goal_location in self.robot.possible_arms) and\
                    self.get_item_locations(self.get_robot_name())[0] not in [start_location, goal_location]:
                raise Exception('Robot can only pick or place objects when he is at the same location as the object:' +
                                ' robot is at {}, moving item from {} to {}.'.
                                format(self.get_item_locations(self.get_robot_name())[0], start_location, goal_location))
        self.remove_item_at_location(item_name, start_location)
        self.add_item_at_location(item_name, goal_location)

    def get_robot_name(self):
        return self.robot.name

    # def object_location_transition_model(self, old_location, new_location, fail_probability):
    #     """
    #     Probability of successful location change is (1 - fail_probability)
    #     :param str old_location: one of FactoryObject.possible_locations
    #     :param str new_location: one of FactoryObject.possible_locations
    #     :param float fail_probability: a number from 0 to 1
    #     :return hpnutil.dist.DDist: a discrete distribution over locations
    #     """
    #     new_location_distribution = hpnutil.dist.DDist({new_location: 1 - fail_probability})
    #     new_location_distribution.addProb(old_location, fail_probability)
    #     return new_location_distribution

    def executePrim(self, operator_name, primitive_arguments):
        """
        :param str operator_name:
        :param primitive_arguments: whatever the primitive of the operator returns
        :return: an observation which results from perceiving the effects of executing the primitive
        """
        if operator_name == 'Go':
            robot_name = primitive_arguments[0]
            start_location = primitive_arguments[1]
            goal_location = primitive_arguments[2]
            self.move_item_or_robot(robot_name, start_location, goal_location)
        elif operator_name == 'ManipulateEnvironment':
            container_name = primitive_arguments[0]
            container_state = primitive_arguments[1]
            self.environment.set_container_state(container_state, container_name)
        elif operator_name == 'PickUp':
            arm = primitive_arguments[0]
            item_name = primitive_arguments[1]
            item_location = primitive_arguments[2]
            self.move_item_or_robot(item_name, item_location, arm)
        elif operator_name == 'Place':
            arm = primitive_arguments[0]
            item_name = primitive_arguments[1]
            item_location = primitive_arguments[2]
            self.move_item_or_robot(item_name, arm, item_location)
        elif operator_name == 'Regrasp':
            current_arm = primitive_arguments[0]
            new_arm = primitive_arguments[1]
            item_name = primitive_arguments[2]
            self.move_item_or_robot(item_name, current_arm, new_arm)
        else:
            raise Exception('Unknown operator primitive {}.'.format(operator_name))

    #     if operator_name in ['Wash', 'Paint', 'Dry']:
    #         object_name = primitive_arguments
    #         new_state_distribution = self.object_state_transition_model(self.object_with_name(object_name).state,
    #                                                                     self.operator_resulting_states[operator_name],
    #                                                                     self.operator_fail_probabilities[operator_name],
    #                                                                     self.relevant_probability)
    #         # self.set_object_state(object_name, self.operator_resulting_states[operator_name])  # object_name, new_state
    #         # instead of simply setting the new expected state as a result of executing the operator,
    #         # draw a random sample from the discrete distribution over states that we get from the state transition model
    #         resulting_state = new_state_distribution.draw()
    #         self.set_object_state(object_name, resulting_state)
    #         return resulting_state  # resulting_state will be our observation
    #     elif operator_name == 'Move':
    #         object_name = primitive_arguments[0]
    #         start_location = primitive_arguments[1]
    #         new_location = primitive_arguments[2]
    #         # change the location
    #         new_location_distribution = self.object_location_transition_model(start_location,
    #                                                                           new_location,
    #                                                                           self.operator_fail_probabilities[
    #                                                                               operator_name])
    #         resulting_location = new_location_distribution.draw()
    #         self.set_object_location(object_name, start_location, resulting_location)
    #         # there is a chance that during moving an object will get dirty
    #         new_state_distribution = self.object_get_dirty_during_move_transition_model(
    #             self.object_with_name(object_name).state,
    #             self.probability_of_getting_dirty_when_moving)
    #         resulting_state = new_state_distribution.draw()
    #         self.set_object_state(object_name, resulting_state)
    #         return resulting_location, resulting_state  # those two are our observations
    #     elif operator_name == 'ExamineLocation':
    #         location = primitive_arguments
    #         return map(lambda obj: obj.name, self.objects_at_location(location))
    #     else:
    #         raise Exception('Unknown operator primitive {}.'.format(operator_name))

    def reset(self, believed_world):
        pass