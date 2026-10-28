from .constants import (Terrain, Obstacle, TERRAIN_SPEED_MULTIPLIERS, TERRAIN_STEAM_RATES , OBSTACLE_STEAM_COSTS)

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


class TrackedSamovar:
    def __validate_string(self, value: any, param_name: str) -> None:
        """Проверяет, что параметр является строкой."""
        if not isinstance(value, str):
            raise TypeError(f"{param_name} must be a string")

    def __validate_number(self, value: any, param_name: str, positive: bool = True) -> float:
        """Проверяет, что параметр — число (не bool) и опционально положительное[cite: 1]."""
        if type(value) not in {int, float}:
            raise TypeError(f"{param_name} must be a number")
        val_float = float(value)
        if positive and val_float <= 0:
            raise ValueError(f"{param_name} must be positive")
        return val_float

    def __validate_move_params(self, distance_km: float, terrain: str) -> float:
        """Общая валидация параметров движения (для move и calculate_steam)."""

        # Проверка расстояния
        dist_float = self.__validate_number(value=distance_km,
                                            param_name="distance_km",
                                            positive=True)

        # Проверка среды
        self.__validate_string(value=terrain,
                               param_name="terrain")

        if terrain not in {t.value for t in Terrain}:
            raise ValueError(f"unknown terrain: {terrain}")

        # 3. Проверка полета
        if terrain == Terrain.AIR:
            raise SamovarCannotFly("samovar cannot fly")

        # 4. Проверка утопления в воде
        if terrain == Terrain.WATER and dist_float > 0.5:
            raise SamovarWouldSink(f"water crossing longer than 0.5 km: {dist_float}")

        return dist_float

    def __get_obstacle_cost_and_validate(self, obstacle: str) -> float:
        """
        Общая логика проверки препятствий (пункты 1–8) и расчета расхода пара.
        Выбрасывает TypeError, ValueError или соответствующие доменные исключения.
        """
        # 1. TypeError — obstacle не str
        self.__validate_string(value=obstacle,
                               param_name="obstacle")

        # 2. ValueError — obstacle не из списка
        if obstacle not in {o.value for o in Obstacle}:
            raise ValueError(f"unknown obstacle: {obstacle}")

        # 3. SamovarStuck — obstacle == "wall"
        if obstacle == Obstacle.WALL:
            raise SamovarStuck("samovar is stuck against the wall")

        # 4. SamovarTracksBroken — tracks_ok == False
        if not self.__tracks_ok:
            raise SamovarTracksBroken("tracks are broken")

        # 5. SamovarStuck — "ditch" и track_width_m < 1.0
        if obstacle == Obstacle.DITCH and self.__track_width_m < 1.0:
            raise SamovarStuck("track width is too narrow for the ditch")

        # 6. SamovarTooWide — "narrow_bridge" и track_width_m > 1.5
        if obstacle == Obstacle.NARROW_BRIDGE and self.__track_width_m > 1.5:
            raise SamovarTooWide("samovar is too wide for the narrow bridge")

        # 7. SamovarTooHeavy — "narrow_bridge" и mass_kg > 1000
        if obstacle == Obstacle.NARROW_BRIDGE and self.__mass_kg > 1000:
            raise SamovarTooHeavy("samovar is too heavy for the narrow bridge")

        # Получаем расход пара (для "boulder" — 10, "ditch" — 5, "narrow_bridge" — 2)
        required_steam = OBSTACLE_STEAM_COSTS[obstacle]

        # 8. SamovarNoSteam — расход больше текущего steam
        if required_steam > self.__steam:
            raise SamovarNoSteam(
                f"not enough steam to overcome {obstacle}: required {required_steam}, have {self.__steam}"
            )

        return required_steam

    def __init__(
        self,
        name: str,
        mass_kg: float,
        track_width_m: float,
        max_speed_kmh: float,
        steam: float = 100.0,
    ) -> None:
        # Валидация name
        self.__validate_string(value=name,
                               param_name="name")
        if not name.strip():
            raise ValueError("name must not be empty")
        self.__name = name

        # Валидация числовых параметров
        self.__mass_kg = self.__validate_number(value=mass_kg,
                                                param_name="mass_kg")
        self.__track_width_m = self.__validate_number(value=track_width_m,
                                                      param_name="track_width_m")
        self.__max_speed_kmh = self.__validate_number(value=max_speed_kmh,
                                                      param_name="max_speed_kmh")

        # Валидация пара (0...100)
        steam_val = self.__validate_number(value=steam,
                                           param_name="steam",
                                           positive=False)
        if not (0 <= steam_val <= 100):
            raise ValueError("steam must be between 0 and 100")
        self.__steam = steam_val

        # Начальное состояние по ТЗ
        self.__position_km = 0.0
        self.__terrain = "ground"
        self.__tracks_ok = True
        self.__cups_served = 0

    # Свойства только для чтения
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

    def calculate_steam(self, distance_km: float, terrain: str) -> float:
        """Рассчитывает расход пара на перемещение без изменения состояния."""
        # Проверки 1–4 (тип, значения, воздух, брод)
        dist_float = self.__validate_move_params(distance_km=distance_km,
                                                 terrain=terrain)

        # Возвращаем расход пара по таблице
        required_steam = dist_float * TERRAIN_STEAM_RATES[terrain]

        return required_steam

    def move(self, distance_km: float, terrain: str) -> float:
        """Перемещает самовар на заданное расстояние в заданной среде"""
        required_steam = self.calculate_steam(distance_km=distance_km,
                                              terrain=terrain)

        # 5. Проверка исправности гусениц
        if not self.__tracks_ok:
            raise SamovarTracksBroken("tracks are broken")

        # 6. Проверка наличия пара
        if required_steam > self.__steam:
            raise SamovarNoSteam(f"not enough steam: required {required_steam}, have {self.__steam}")

        # Расчет времени и изменение состояния
        dist_float = float(distance_km)
        speed = self.__max_speed_kmh * TERRAIN_SPEED_MULTIPLIERS[terrain]
        time_h = dist_float / speed

        self.__position_km += dist_float
        self.__steam -= required_steam
        if self.__steam < 0:
            self.__steam = 0.0
        self.__terrain = terrain

        return time_h

    def overcome(self, obstacle: str) -> None:
        """Преодолевает препятствие, расходуя пар. Меняет только steam."""
        # Получаем требуемый пар (если что-то не так, выбросится нужное исключение)
        required_steam = self.__get_obstacle_cost_and_validate(obstacle=obstacle)

        # Изменяем только steam, позиция и среда не меняются
        self.__steam -= required_steam
        if self.__steam < 0:
            self.__steam = 0.0

    def can_overcome(self, obstacle: str) -> bool:
        """Проверяет, сможет ли самовар преодолеть препятствие в текущем состоянии (без изменения состояния)."""
        try:
            # Ошибки типа (TypeError) и значения (ValueError) пролетят наружу,
            # а любые доменные исключения (SamovarError) будут перехвачены и дадут False.
            self.__get_obstacle_cost_and_validate(obstacle=obstacle)
            return True
        except SamovarError:
            return False

    def damage_tracks(self) -> None:
        """Событие среды (камнепад, острые скалы) — рвёт гусеницы. Повторный вызов безопасен."""
        self.__tracks_ok = False

    def repair_tracks(self) -> None:
        """Машинист чинит гусеницы, затрачивая 20 единиц пара."""
        # Если гусеницы уже исправны — ничего не происходит, пар не тратится
        if self.__tracks_ok:
            return

        repair_cost = 20.0

        # Если пара меньше 20 — бросаем исключение, состояние не меняется
        if self.__steam < repair_cost:
            raise SamovarNoSteam(
                f"not enough steam to repair tracks: required {repair_cost}, have {self.__steam}"
            )

        # Тратим пар и чиним гусеницы
        self.__steam -= repair_cost
        if self.__steam < 0:
            self.__steam = 0.0
        self.__tracks_ok = True

    def brew_tea(self, cups: int) -> float:
        """Заваривает чай, расходуя пар и увеличивая счетчик поданных чашек."""
        if type(cups) is not int:
            raise TypeError(f"cups must be an int, got {type(cups).__name__}")

        # 2. ValueError — cups вне диапазона 1…10
        if not (1 <= cups <= 10):
            raise ValueError(f"cups must be between 1 and 10, got {cups}")

        required_steam = float(cups * 3)

        # 3. SamovarNoSteam — расход больше текущего steam
        if required_steam > self.__steam:
            raise SamovarNoSteam(
                f"not enough steam to brew tea: required {required_steam}, have {self.__steam}"
            )

        # Изменяем состояние: списываем пар и увеличиваем количество поданных чашек
        self.__steam -= required_steam
        if self.__steam < 0:
            self.__steam = 0.0
        self.__cups_served += cups

        return required_steam

    def refuel(self, amount: float) -> None:
        """Пополняет запас пара, подбрасывая шишки в топку (максимум 100)."""
        # 1. TypeError — amount не число или bool
        # Проверяем, что это int или float, но НЕ bool (так как bool в Python — подкласс int)
        if type(amount) not in {int, float}:
            raise TypeError(
                f"amount must be an int or float, got {type(amount).__name__}"
            )

        # Превращаем во float для единообразия
        amount_float = float(amount)

        # 2. ValueError — amount <= 0
        if amount_float <= 0:
            raise ValueError(f"amount must be greater than 0, got {amount_float}")

        # Пополняем пар, но не больше максимального значения (100.0)
        self.__steam = min(100.0, self.__steam + amount_float)

    def get_status(self) -> dict:
        """Возвращает новый словарь со снимком текущего состояния самовара."""
        kwargs = {
            "name": self.__name,
            "steam": float(self.__steam),
            "position_km": float(self.__position_km),
            "terrain": str(self.__terrain),
            "tracks_ok": bool(self.__tracks_ok),
            "cups_served": int(self.__cups_served),
            "track_width_m": float(self.__track_width_m),
        }

        return kwargs
