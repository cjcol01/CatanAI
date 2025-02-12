from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from .enums import ResourceType, DevCardType, GamePhase, TurnPhase, PlacementType
from .player import Player
from .board import Board

@dataclass
class GameState:
    """tracks the entire game state"""
    # core game components
    board: Board
    players: List[Player]
    current_player_index: int
    game_phase: GamePhase
    setup_phase: int
    setup_direction: int
    settlements: Dict[Tuple[int, int], int]  
    roads: Dict[Tuple[Tuple[int, int], Tuple[int, int]], int]
    cities: Dict[Tuple[int, int], int]
    placement_mode: bool
    placement_type: PlacementType
    dice_rolled: bool
    hover_distance: int
    
    # optional stuff with defaults
    setup_turns_completed: int = 0
    robber_position: int = 0
    dice_value: Optional[int] = None
    longest_road_holder: Optional[int] = None
    largest_army_holder: Optional[int] = None
    hovered_corner: Optional[Tuple[int, int]] = None
    hovered_road: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    hovered_city: Optional[Tuple[int, int]] = None
    hovered_settlement: Optional[Tuple[int, int]] = None
    dev_card_deck: List[DevCardType] = field(default_factory=list)

    def __post_init__(self):
        """make sure we have a deck"""
        if self.dev_card_deck is None:
            self.dev_card_deck = []
            
    def to_dict(self) -> Dict:
        """convert state to dict for ai processing"""
        return {
            "players": [self._player_to_dict(p) for p in self.players],
            "current_player": self.current_player_index,
            "game_phase": self.game_phase.name,
            "board": self._board_to_dict(),
            "buildings": {
                "settlements": {str(pos): player_idx for pos, player_idx in self.settlements.items()},
                "cities": {str(pos): player_idx for pos, player_idx in self.cities.items()},
                "roads": {str(pos): player_idx for pos, player_idx in self.roads.items()}
            },
            "turn_status": {
                "dice_value": self.dice_value,
                "dice_rolled": self.dice_rolled,
                "placement_mode": self.placement_mode
            },
            "special_cards": {
                "longest_road": self.longest_road_holder,
                "largest_army": self.largest_army_holder
            }
        }

    def _player_to_dict(self, player: Player) -> Dict:
        """get player info as dict"""
        return {
            "resources": {r.name: amt for r, amt in player.resources.items()},
            "dev_cards": {c.name: amt for c, amt in player.dev_cards.items()},
            "victory_points": {
                "visible": player.visible_victory_points,
                "hidden": player.hidden_victory_points,
                "total": player.calculate_total_victory_points()
            }
        }

    def _board_to_dict(self) -> Dict:
        """get board info as dict"""
        return {
            "tiles": [
                {
                    "position": self.board.axial_layout[i],
                    "resource": tile.resource_type.name,
                    "value": tile.value,
                    "has_robber": i == self.robber_position
                }
                for i, tile in enumerate(self.board.tiles)
            ]
        }