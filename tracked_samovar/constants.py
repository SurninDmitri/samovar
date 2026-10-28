from enum import Enum

class Terrain(str, Enum):
    GROUND = "ground"
    SAND = "sand"
    UNDERGROUND = "underground"
    WATER = "water"
    AIR = "air"


class Obstacle(str, Enum):
    DITCH = "ditch"
    BOULDER = "boulder"
    NARROW_BRIDGE = "narrow_bridge"
    WALL = "wall"

TERRAIN_SPEED_MULTIPLIERS = {
    "ground": 1.0,
    "sand": 0.5,
    "underground": 0.25,
    "water": 0.25,
}

TERRAIN_STEAM_RATES = {
    "ground": 1.0,
    "sand": 2.0,
    "underground": 4.0,
    "water": 3.0,
}

OBSTACLE_STEAM_COSTS = {
    "ditch": 5.0,
    "boulder": 10.0,
    "narrow_bridge": 2.0,
}