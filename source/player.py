from typing import Dict, List, Tuple
from .enums import ResourceType, DevCardType
import random

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
        self.has_longest_road = False
        self.has_largest_army = False
        self.visible_victory_points = 0 
        self.hidden_victory_points = 0    # from dev cards

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

    def can_afford_city(self) -> bool:
        """Check if player has resources for a city."""
        return (self.resources.get(ResourceType.GRAIN, 0) >= 2 and 
                self.resources.get(ResourceType.ORE, 0) >= 3)

    def build_settlement(self, position: Tuple[int, int]):
        self.settlements.append(position)
        self.visible_victory_points = self.calculate_visible_victory_points()

    def build_city(self, position: Tuple[int, int]):
        if position in self.settlements:
            self.settlements.remove(position)
            self.cities.append(position)
        self.visible_victory_points = self.calculate_visible_victory_points()
        
    def build_road(self, start: int, end: int):
        self.roads.append((start, end))

    def get_resource_count(self) -> int:
        return sum(self.resources.values())

    def get_dev_card_count(self) -> int:
        return sum(self.dev_cards.values())
    
    def can_afford_dev(self):
        return (self.resources.get(ResourceType.GRAIN, 0) >= 1 and 
                self.resources.get(ResourceType.ORE, 0) >= 1 and
                self.resources.get(ResourceType.WOOL, 0) >= 1)
    
    def calculate_building_points(self) -> int:
        points = len(self.settlements) + (len(self.cities) * 2)
        print(f"{self.name} has {len(self.settlements)} settlements and {len(self.cities)} cities for {points} points\n")
        return points

        
    def calculate_total_victory_points(self) -> int:
        """Calculate total victory points including hidden ones"""
        points = self.calculate_building_points()
        points += 2 if self.has_longest_road else 0
        points += 2 if self.has_largest_army else 0
        points += self.hidden_victory_points
        return points
    
    def calculate_visible_victory_points(self) -> int:
        """Calculate victory points visible to other players"""
        points = self.calculate_building_points()
        points += 2 if self.has_longest_road else 0
        points += 2 if self.has_largest_army else 0
        return points