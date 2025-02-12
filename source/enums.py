from enum import Enum, auto

# !!! Comments AI generated !!!
class ResourceType(Enum):
    """
    Represents the different types of resources in Catan.
    WOOD: Used for building roads and settlements
    BRICK: Used for building roads and settlements
    ORE: Used for building cities and buying development cards
    GRAIN: Used for building cities and buying development cards
    WOOL: Used for buying development cards
    DESERT: Produces no resources and starts with the robber
    """
    WOOD = auto()
    BRICK = auto()
    ORE = auto()
    GRAIN = auto()
    WOOL = auto()
    DESERT = auto()

class DevCardType(Enum):
    """
    Represents the different types of development cards in Catan.
    KNIGHT: Allows moving the robber and counts towards largest army
    ROAD_BUILDING: Allows building two roads for free
    YEAR_OF_PLENTY: Take any two resources from the bank
    MONOPOLY: Name a resource and take all of that type from other players
    VICTORY_POINT: Worth one victory point
    """
    KNIGHT = auto()
    ROAD_BUILDING = auto()
    YEAR_OF_PLENTY = auto()
    MONOPOLY = auto()
    VICTORY_POINT = auto()

class GamePhase(Enum):
    """
    Represents the different states of the game.
    SETUP: Initial phase where players place their first settlements and roads
    PLAY: Main game phase where players take turns and perform actions
    END: Game is over, winner has been determined
    """
    SETUP = auto()
    PLAY = auto()
    END = auto()

class PlayerAction(Enum):
    """
    Represents the different actions a player can take during their turn.
    BUILD_SETTLEMENT: Build a new settlement (costs 1 wood, 1 brick, 1 grain, 1 wool)
    BUILD_CITY: Upgrade a settlement to a city (costs 2 grain and 3 ore)
    BUILD_ROAD: Build a road connecting settlements (costs 1 wood, 1 brick)
    BUY_DEV_CARD: Purchase a development card (costs 1 ore, 1 grain, 1 wool)
    PLAY_DEV_CARD: Play a previously purchased development card
    TRADE: Trade resources with other players or the bank
    END_TURN: End the current player's turn
    """
    BUILD_SETTLEMENT = auto()
    BUILD_CITY = auto()
    BUILD_ROAD = auto()
    BUY_DEV_CARD = auto()
    PLAY_DEV_CARD = auto()
    TRADE = auto()
    END_TURN = auto()

class PlacementType(Enum):
    """
    Represents the different types of pieces that can be placed on the board.
    SETTLEMENT: A settlement worth 1 victory point
    ROAD: A road connecting settlements/cities
    CITY: An upgraded settlement worth 2 victory points
    """
    SETTLEMENT = auto()
    ROAD = auto()
    CITY = auto()

class TurnPhase(Enum):
    PRE_ROLL = auto()    # beginning of turn, can play dev cards
    ROBBER = auto()      # after rolling 7, must move robber
    POST_ROLL = auto()   # after rolling, can build/trade/etc
    TRADING = auto()     # during trade negotiation
    END = auto()         # turn is complete