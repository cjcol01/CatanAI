from typing import Dict, List, Tuple
from .enums import ResourceType, DevCardType

class Player:
    def __init__(self, color: Tuple[int, int, int], name: str):
        self.color = color
        self.name = name
        self.resources: Dict[ResourceType, int] = {rt: 0 for rt in ResourceType if rt != ResourceType.DESERT}
        self.dev_cards: Dict[DevCardType, int] = {dt: 0 for dt in DevCardType}
        self.settlements: List[int] = []
        self.cities: List[int] = []
        self.roads: List[Tuple[int, int]] = []
        self.knights_played: int = 0
        self.victory_points: int = 0

    def add_resource(self, resource_type: ResourceType, amount: int = 1):
        self.resources[resource_type] += amount

    def remove_resource(self, resource_type: ResourceType, amount: int = 1) -> bool:
        if self.resources[resource_type] >= amount:
            self.resources[resource_type] -= amount
            return True
        return False

    def has_resources(self, required_resources: Dict[ResourceType, int]) -> bool:
        return all(self.resources[rt] >= amount for rt, amount in required_resources.items())

    def spend_resources(self, required_resources: Dict[ResourceType, int]) -> bool:
        if self.has_resources(required_resources):
            for rt, amount in required_resources.items():
                self.resources[rt] -= amount
            return True
        return False

    def can_afford_settlement(self) -> bool:
        return self.has_resources({
            ResourceType.WOOD: 1,
            ResourceType.BRICK: 1,
            ResourceType.GRAIN: 1,
            ResourceType.WOOL: 1
        })

    def can_afford_road(self) -> bool:
        return self.has_resources({
            ResourceType.WOOD: 1,
            ResourceType.BRICK: 1
        })

    def build_settlement(self, position: int):
        self.settlements.append(position)
        self.victory_points += 1

    def build_city(self, position: int):
        if position in self.settlements:
            self.settlements.remove(position)
            self.cities.append(position)
            self.victory_points += 1

    def build_road(self, start: int, end: int):
        self.roads.append((start, end))

    def get_resource_count(self) -> int:
        return sum(self.resources.values())

    def get_dev_card_count(self) -> int:
        return sum(self.dev_cards.values())