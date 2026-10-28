"""Гусеничный самовар «Пыхтун» (SPEC v0.2)."""

from __future__ import annotations

import math
from enum import Enum
from typing import Any


class CrazyVehicleError(RuntimeError):
    """Базовое исключение для всего безумного транспорта."""
    pass


class SamovarError(CrazyVehicleError):
    """Базовое исключение для гусеничного самовара «Пыхтун»."""
    pass


class SamovarCannotFly(SamovarError):
    """Самовар пытается лететь."""
    pass


class SamovarWouldSink(SamovarError):
    """Самовар тонет (слишком глубокий брод)."""
    pass


class SamovarTracksBroken(SamovarError):
    """Движение или препятствие при порванных гусеницах."""
    pass


class SamovarNoSteam(SamovarError):
    """Не хватает пара для действия."""
    pass


class SamovarStuck(SamovarError):
    """Самовар застрял (стена или слишком узкие гусеницы для канавы)."""
    pass


class SamovarTooWide(SamovarError):
    """Гусеницы слишком широкие для узкого моста."""
    pass


class SamovarTooHeavy(SamovarError):
    """Самовар слишком тяжелый для узкого моста."""
    pass


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


class TrackedSamovar:
    def __init__(
        self,
        name: str,
        mass_kg: float,
        track_width_m: float,
        max_speed_kmh: float,
        steam: float = 100.0,
    ) -> None:
        self.__validate_string(name, "name")
        if not name.strip():
            raise ValueError("name must not be empty")
        mass_kg_f = self.__validate_number_finite_positive(mass_kg, "mass_kg")
        track_width_m_f = self.__validate_number_finite_positive(track_width_m, "track_width_m")
        max_speed_kmh_f = self.__validate_number_finite_positive(max_speed_kmh, "max_speed_kmh")
        steam_f = self.__validate_number_finite_range(steam, "steam", 0.0, 100.0)

        self.__name = name
        self.__mass_kg = float(mass_kg_f)
        self.__track_width_m = float(track_width_m_f)
        self.__max_speed_kmh = float(max_speed_kmh_f)
        self.__steam = float(steam_f)

        self.__position_km = 0.0
        self.__terrain = "ground"
        self.__tracks_ok = True
        self.__cups_served = 0

    def __validate_string(self, value: Any, param_name: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{param_name} must be a string")

    def __is_number(self, value: Any) -> bool:
        if isinstance(value, bool):
            return False
        return isinstance(value, (int, float))

    def __validate_number_finite(self, value: Any, param_name: str) -> float:
        if not self.__is_number(value):
            raise TypeError(f"{param_name} must be a number")
        try:
            val_float = float(value)
        except Exception as exc:
            raise ValueError(f"{param_name} must be finite") from exc
        if not math.isfinite(val_float):
            raise ValueError(f"{param_name} must be finite")
        return val_float

    def __validate_number_finite_positive(self, value: Any, param_name: str) -> float:
        val = self.__validate_number_finite(value, param_name)
        if val <= 0:
            raise ValueError(f"{param_name} must be positive")
        return val

    def __validate_number_finite_range(
        self, value: Any, param_name: str, low: float, high: float
    ) -> float:
        val = self.__validate_number_finite(value, param_name)
        if val < low or val > high:
            raise ValueError(f"{param_name} must be between {low} and {high}")
        return val

    @property
    def name(self) -> str:
        return self.__name

    @property
    def mass_kg(self) -> float:
        return self.__mass_kg

    @property
    def track_width_m(self) -> float:
        return self.__track_width_m

    @property
    def max_speed_kmh(self) -> float:
        return self.__max_speed_kmh

    @property
    def steam(self) -> float:
        return self.__steam

    @property
    def position_km(self) -> float:
        return self.__position_km

    @property
    def terrain(self) -> str:
        return self.__terrain

    @property
    def tracks_ok(self) -> bool:
        return self.__tracks_ok

    @property
    def cups_served(self) -> int:
        return self.__cups_served

    def __validate_move_params(self, distance_km: Any, terrain: Any) -> float:
        # 1. Сначала типы обоих параметров.
        if not self.__is_number(distance_km):
            raise TypeError("distance_km must be a number")
        if not isinstance(terrain, str):
            raise TypeError("terrain must be a string")

        # 2. Затем значения параметров.
        try:
            dist_float = float(distance_km)
        except Exception as exc:
            raise ValueError("distance_km must be finite") from exc
        if not math.isfinite(dist_float):
            raise ValueError("distance_km must be finite")
        if dist_float <= 0:
            raise ValueError("distance_km must be positive")

        if terrain not in {t.value for t in Terrain}:
            raise ValueError(f"unknown terrain: {terrain}")

        # 3-4. Доменные проверки среды.
        if terrain == Terrain.AIR:
            raise SamovarCannotFly("samovar cannot fly")
        if terrain == Terrain.WATER and dist_float > 0.5:
            raise SamovarWouldSink(
                f"water crossing longer than 0.5 km: {dist_float}"
            )

        return dist_float

    def calculate_steam(self, distance_km: float, terrain: str) -> float:
        dist_float = self.__validate_move_params(distance_km, terrain)
        required_steam = dist_float * TERRAIN_STEAM_RATES[terrain]
        return required_steam

    def move(self, distance_km: float, terrain: str) -> float:
        required_steam = self.calculate_steam(distance_km, terrain)

        if not self.__tracks_ok:
            raise SamovarTracksBroken("tracks are broken")

        if required_steam > self.__steam:
            raise SamovarNoSteam(
                f"not enough steam: required {required_steam}, have {self.__steam}"
            )

        dist_float = float(distance_km)
        speed = self.__max_speed_kmh * TERRAIN_SPEED_MULTIPLIERS[terrain]
        time_h = dist_float / speed

        self.__position_km += dist_float
        self.__steam -= required_steam
        if self.__steam < 0:
            self.__steam = 0.0
        self.__terrain = terrain

        return time_h

    def __validate_obstacle_name(self, obstacle: Any) -> None:
        self.__validate_string(obstacle, "obstacle")
        if obstacle not in {o.value for o in Obstacle}:
            raise ValueError(f"unknown obstacle: {obstacle}")

    def __obstacle_cost(self, obstacle: str) -> float:
        return OBSTACLE_STEAM_COSTS[obstacle]

    def __check_obstacle_rules(self, obstacle: str) -> None:
        if obstacle == Obstacle.WALL:
            raise SamovarStuck("wall")

        if not self.__tracks_ok:
            raise SamovarTracksBroken("tracks are broken")

        if obstacle == Obstacle.DITCH and self.__track_width_m < 1.0:
            raise SamovarStuck("track width too small for ditch")

        if obstacle == Obstacle.NARROW_BRIDGE:
            if self.__track_width_m > 1.5:
                raise SamovarTooWide("tracks too wide for narrow bridge")
            if self.__mass_kg > 1000:
                raise SamovarTooHeavy("too heavy for narrow bridge")

    def can_overcome(self, obstacle: str) -> bool:
        self.__validate_obstacle_name(obstacle)
        try:
            self.__check_obstacle_rules(obstacle)
        except SamovarError:
            return False
        cost = self.__obstacle_cost(obstacle)
        return cost <= self.__steam

    def overcome(self, obstacle: str) -> None:
        self.__validate_obstacle_name(obstacle)
        self.__check_obstacle_rules(obstacle)
        cost = self.__obstacle_cost(obstacle)
        if cost > self.__steam:
            raise SamovarNoSteam(
                f"not enough steam: required {cost}, have {self.__steam}"
            )
        self.__steam -= cost
        if self.__steam < 0:
            self.__steam = 0.0

    def damage_tracks(self) -> None:
        self.__tracks_ok = False

    def repair_tracks(self) -> None:
        if self.__tracks_ok:
            return
        repair_cost = 20.0
        if self.__steam < repair_cost:
            raise SamovarNoSteam(
                f"not enough steam to repair tracks: required {repair_cost}, have {self.__steam}"
            )
        self.__steam -= repair_cost
        if self.__steam < 0:
            self.__steam = 0.0
        self.__tracks_ok = True

    def brew_tea(self, cups: int) -> float:
        if isinstance(cups, bool) or not isinstance(cups, int):
            raise TypeError("cups must be an int")
        if cups < 1 or cups > 10:
            raise ValueError("cups must be between 1 and 10")
        required_steam = float(cups) * 3.0
        if required_steam > self.__steam:
            raise SamovarNoSteam(
                f"not enough steam: required {required_steam}, have {self.__steam}"
            )
        self.__steam -= required_steam
        if self.__steam < 0:
            self.__steam = 0.0
        self.__cups_served += cups
        return required_steam

    def refuel(self, amount: float) -> None:
        amount_f = self.__validate_number_finite_positive(amount, "amount")
        if self.__steam >= 100.0:
            return
        self.__steam += amount_f
        if self.__steam >= 100.0:
            self.__steam = 100.0

    def get_status(self) -> dict:
        return {
            "name": self.__name,
            "steam": self.__steam,
            "position_km": self.__position_km,
            "terrain": self.__terrain,
            "tracks_ok": self.__tracks_ok,
            "cups_served": self.__cups_served,
            "track_width_m": self.__track_width_m,
        }
