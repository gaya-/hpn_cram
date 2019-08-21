
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

    @classmethod
    def to_world_state(cls, robot):
        items_in_hands_copy = {}
        for (hand, item) in robot.items_in_hands.items():
            items_in_hands_copy[hand] = WorldStateItem.to_world_state(item) if item else None
        world_state_robot = cls(robot.name, items_in_hands_copy)
        return world_state_robot


class WorldStateEnvironment(Environment):
    def __init__(self, name, items_at_locations=None, container_states=None):
        Environment.__init__(self, name, items_at_locations, container_states)

    @classmethod
    def to_world_state(cls, environment):
        items_at_locations_copy = {}
        for (location, items_list) in environment.items_at_locations.items():
            items_at_locations_copy[location] = map(lambda item: WorldStateItem.to_world_state(item), items_list)
        container_states_copy = copy.copy(environment.container_states)
        world_state_environment = cls(environment.name, items_at_locations_copy, container_states_copy)
        return world_state_environment


class WorldState(World):
    def __init__(self, environment, robot, operator_fail_probabilities):
        World.__init__(self, environment, robot, operator_fail_probabilities)

    @classmethod
    def to_world_state(cls, world):
        world_state = cls(WorldStateEnvironment.to_world_state(world.environment),
                          WorldStateRobot.to_world_state(world.robot),
                          copy.copy(world.operator_fail_probabilities))
        return world_state