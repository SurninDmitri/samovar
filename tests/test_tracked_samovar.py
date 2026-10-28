"""Тесты для «Гусеничного самовара «Пыхтун»» (SPEC.md, TEST_CASES.md).

Автор ТЗ и тестов: Игнатьева Мария Сергеевна (роль A).

Модульные тесты (TC-01 … TC-22) написаны по паттерну AAA
(Arrange / Act / Assert). Сценарные тесты (TC-23 … TC-26) написаны
по паттерну GWT (Given / When / Then) через обёртку «Машинист».

Каждый тест-метод содержит ID своего TC в имени и в docstring.

Запуск из корня репозитория:
    python -m unittest discover -s tests -v
"""

import unittest

from tracked_samovar.tracked_samovar import (
    CrazyVehicleError,
    SamovarCannotFly,
    SamovarError,
    SamovarNoSteam,
    SamovarStuck,
    SamovarTooHeavy,
    SamovarTooWide,
    SamovarTracksBroken,
    SamovarWouldSink,
    TrackedSamovar,
)

PLACES = 7  # точность сравнения float (см. SPEC, раздел 3.0)
NAN = float("nan")
INF = float("inf")
HUGE_INT = 10**400  # не переводится во float без переполнения

DOMAIN_EXCEPTIONS = (
    SamovarCannotFly,
    SamovarWouldSink,
    SamovarTracksBroken,
    SamovarNoSteam,
    SamovarStuck,
    SamovarTooWide,
    SamovarTooHeavy,
)


def make_samovar(**overrides):
    """Создаёт эталонный самовар «Пыхтун»; любые параметры можно переопределить."""
    params = {
        "name": "Пыхтун",
        "mass_kg": 800.0,
        "track_width_m": 1.2,
        "max_speed_kmh": 20.0,
        "steam": 100.0,
    }
    params.update(overrides)
    return TrackedSamovar(**params)


def shown(value):
    """Короткая подпись для subTest: 10**400 не печатается целиком."""
    if isinstance(value, tuple):
        return tuple(shown(item) for item in value)
    return "10**400" if value is HUGE_INT else value


def snapshot(samovar):
    """Наблюдаемое состояние самовара — для проверки «состояние не изменилось»."""
    return (
        samovar.steam,
        samovar.position_km,
        samovar.terrain,
        samovar.tracks_ok,
        samovar.cups_served,
    )


# ---------------------------------------------------------------------------
# Доменная обёртка для сценарных тестов (SPEC, раздел 4.2)
# ---------------------------------------------------------------------------

class Машинист:
    """Эмулятор машиниста. Управляет самоваром на доменном языке."""

    def __init__(self, samovar):
        self._samovar = samovar

    def ехать(self, distance_km):
        return self._samovar.move(distance_km, "ground")

    def ехать_по_песку(self, distance_km):
        return self._samovar.move(distance_km, "sand")

    def бурить(self, distance_km):
        return self._samovar.move(distance_km, "underground")

    def вброд(self, distance_km):
        return self._samovar.move(distance_km, "water")

    def взлететь(self, distance_km=1):
        return self._samovar.move(distance_km, "air")

    def прикинуть(self, distance_km, terrain):
        return self._samovar.calculate_steam(distance_km, terrain)

    def может(self, obstacle):
        return self._samovar.can_overcome(obstacle)

    def перескочить_канаву(self):
        self._samovar.overcome("ditch")

    def столкнуть_валун(self):
        self._samovar.overcome("boulder")

    def переехать_мост(self):
        self._samovar.overcome("narrow_bridge")

    def штурмовать_стену(self):
        self._samovar.overcome("wall")

    def заварить_чай(self, cups):
        return self._samovar.brew_tea(cups)

    def подбросить_шишек(self, amount):
        self._samovar.refuel(amount)

    def починить_гусеницы(self):
        self._samovar.repair_tracks()

    def доложить(self):
        return self._samovar.get_status()


class Камнепад:
    """Событие среды: камни падают на самовар и рвут гусеницы."""

    def обрушиться_на(self, samovar):
        samovar.damage_tracks()


# ---------------------------------------------------------------------------
# Модульные тесты (AAA)
# ---------------------------------------------------------------------------

class TestConstructor(unittest.TestCase):

    def test_tc01_init_stores_parameters_and_initial_state(self):
        """TC-01: конструктор сохраняет параметры и задаёт начальное состояние."""
        # Arrange / Act
        samovar = TrackedSamovar("Пыхтун", 800.0, 1.2, 20.0)

        # Assert
        self.assertEqual(samovar.name, "Пыхтун")
        self.assertAlmostEqual(samovar.mass_kg, 800.0, places=PLACES)
        self.assertAlmostEqual(samovar.track_width_m, 1.2, places=PLACES)
        self.assertAlmostEqual(samovar.max_speed_kmh, 20.0, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 100.0, places=PLACES)
        self.assertAlmostEqual(samovar.position_km, 0.0, places=PLACES)
        self.assertEqual(samovar.terrain, "ground")
        self.assertIs(samovar.tracks_ok, True)
        self.assertEqual(samovar.cups_served, 0)

        for steam in (0, 0.0, 100, 100.0):
            with self.subTest(steam=steam):
                self.assertAlmostEqual(
                    make_samovar(steam=steam).steam, float(steam), places=PLACES
                )

        # подклассы int и float считаются числами и приводятся к float
        class Kilograms(float):
            pass

        class Kmh(int):
            pass

        converted = TrackedSamovar("Пыхтун", Kilograms(800.0), 1.2, Kmh(20))
        self.assertIs(type(converted.mass_kg), float)
        self.assertIs(type(converted.max_speed_kmh), float)
        self.assertAlmostEqual(converted.max_speed_kmh, 20.0, places=PLACES)

    def test_tc02_init_empty_name_raises(self):
        """TC-02: пустое имя или имя из пробелов -> ValueError."""
        for name in ("", "   ", "\t\n"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    make_samovar(name=name)

    def test_tc03_init_nonpositive_dimensions_raise(self):
        """TC-03: mass_kg, track_width_m, max_speed_kmh <= 0 или неконечны -> ValueError."""
        for param in ("mass_kg", "track_width_m", "max_speed_kmh"):
            for value in (0, 0.0, -1.0, NAN, INF, -INF, HUGE_INT):
                with self.subTest(param=param, value=shown(value)):
                    with self.assertRaises(ValueError):
                        make_samovar(**{param: value})

    def test_tc04_init_steam_out_of_range_raises(self):
        """TC-04: steam вне диапазона 0…100 или неконечен -> ValueError."""
        for steam in (-0.1, 100.1, 1000, NAN, INF, -INF):
            with self.subTest(steam=steam):
                with self.assertRaises(ValueError):
                    make_samovar(steam=steam)

    def test_tc05_init_wrong_types_raise(self):
        """TC-05: неверные типы параметров конструктора -> TypeError."""
        cases = [
            {"name": 123},
            {"name": None},
            {"mass_kg": "800"},
            {"track_width_m": None},
            {"max_speed_kmh": [20]},
            {"steam": True},
            {"mass_kg": False},
        ]
        for overrides in cases:
            with self.subTest(**{k: repr(v) for k, v in overrides.items()}):
                with self.assertRaises(TypeError):
                    make_samovar(**overrides)

    def test_tc06_public_attributes_are_read_only(self):
        """TC-06: прямое присваивание публичным атрибутам -> AttributeError."""
        # Arrange
        samovar = make_samovar()
        new_values = {
            "name": "Другой",
            "mass_kg": 1.0,
            "track_width_m": 1.0,
            "max_speed_kmh": 1.0,
            "steam": 1.0,
            "position_km": 1.0,
            "terrain": "sand",
            "tracks_ok": False,
            "cups_served": 1,
        }
        for attr, value in new_values.items():
            with self.subTest(attr=attr):
                # Act / Assert
                with self.assertRaises(AttributeError):
                    setattr(samovar, attr, value)


class TestMove(unittest.TestCase):

    def test_tc07_move_by_terrain(self):
        """TC-07: move считает время, расход пара, позицию и среду для каждой среды."""
        # terrain, distance, ожидаемое время (ч), ожидаемый пар после
        cases = [
            ("ground", 10.0, 0.5, 90.0),        # 10 / 20;  100 - 10*1
            ("sand", 5.0, 0.5, 90.0),           # 5 / 10;   100 - 5*2
            ("underground", 5.0, 1.0, 80.0),    # 5 / 5;    100 - 5*4
            ("water", 0.5, 0.1, 98.5),          # 0.5 / 5;  100 - 0.5*3
        ]
        for terrain, distance, hours, steam_after in cases:
            with self.subTest(terrain=terrain):
                # Arrange
                samovar = make_samovar()

                # Act
                result = samovar.move(distance, terrain)

                # Assert
                self.assertIsInstance(result, float)
                self.assertAlmostEqual(result, hours, places=PLACES)
                self.assertAlmostEqual(samovar.steam, steam_after, places=PLACES)
                self.assertAlmostEqual(samovar.position_km, distance, places=PLACES)
                self.assertEqual(samovar.terrain, terrain)

    def test_tc08_move_invalid_arguments_raise(self):
        """TC-08: некорректные аргументы move -> ValueError / TypeError, состояние не меняется."""
        cases = [
            ((0, "ground"), ValueError),
            ((-5, "ground"), ValueError),
            ((1, "lava"), ValueError),
            ((1, ""), ValueError),
            ((NAN, "ground"), ValueError),
            ((INF, "ground"), ValueError),
            ((-INF, "ground"), ValueError),
            ((HUGE_INT, "ground"), ValueError),
            (("abc", "ground"), TypeError),
            ((True, "ground"), TypeError),
            ((None, "ground"), TypeError),
            ((1, 1), TypeError),
        ]
        for args, exc in cases:
            with self.subTest(args=shown(args)):
                # Arrange
                samovar = make_samovar()
                before = snapshot(samovar)

                # Act / Assert
                with self.assertRaises(exc):
                    samovar.move(*args)
                self.assertEqual(snapshot(samovar), before)

    def test_tc09_move_air_and_deep_water_raise(self):
        """TC-09: "air" -> SamovarCannotFly; вода > 0.5 км -> SamovarWouldSink."""
        cases = [
            ((1, "air"), SamovarCannotFly),
            ((0.6, "water"), SamovarWouldSink),
            ((0.5000001, "water"), SamovarWouldSink),
        ]
        for args, exc in cases:
            with self.subTest(args=shown(args)):
                # Arrange
                samovar = make_samovar()
                before = snapshot(samovar)

                # Act / Assert
                with self.assertRaises(exc):
                    samovar.move(*args)
                self.assertEqual(snapshot(samovar), before)

    def test_tc10_move_not_enough_steam_raises(self):
        """TC-10: пара меньше, чем нужно -> SamovarNoSteam, состояние не меняется."""
        # Arrange
        samovar = make_samovar(steam=20.0)
        before = snapshot(samovar)

        # Act / Assert
        with self.assertRaises(SamovarNoSteam):
            samovar.move(30, "ground")
        self.assertEqual(snapshot(samovar), before)

    def test_tc11_move_spends_exactly_all_steam(self):
        """TC-11: пара хватает ровно на поездку -> поездка успешна, steam == 0."""
        # Arrange
        samovar = make_samovar(steam=20.0)

        # Act
        hours = samovar.move(20, "ground")

        # Assert
        self.assertAlmostEqual(hours, 1.0, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 0.0, places=PLACES)
        self.assertAlmostEqual(samovar.position_km, 20.0, places=PLACES)

    def test_tc12_move_with_broken_tracks_raises(self):
        """TC-12: гусеницы порваны -> SamovarTracksBroken, состояние не меняется."""
        # Arrange
        samovar = make_samovar()
        samovar.damage_tracks()
        before = snapshot(samovar)

        # Act / Assert
        for terrain in ("ground", "sand", "underground", "water"):
            with self.subTest(terrain=terrain):
                with self.assertRaises(SamovarTracksBroken):
                    samovar.move(0.5, terrain)
                self.assertEqual(snapshot(samovar), before)


class TestCalculateSteam(unittest.TestCase):

    def test_tc13_calculate_steam(self):
        """TC-13: calculate_steam считает расход, не меняет состояние, не зависит от пара и гусениц."""
        cases = [
            ("ground", 10.0, 10.0),
            ("sand", 5.0, 10.0),
            ("underground", 5.0, 20.0),
            ("water", 0.5, 1.5),
        ]
        # Arrange: пара нет, гусеницы порваны — расчёт всё равно возможен
        samovar = make_samovar(steam=0.0)
        samovar.damage_tracks()
        before = snapshot(samovar)

        for terrain, distance, expected in cases:
            with self.subTest(terrain=terrain):
                # Act
                cost = samovar.calculate_steam(distance, terrain)

                # Assert
                self.assertIsInstance(cost, float)
                self.assertAlmostEqual(cost, expected, places=PLACES)
                self.assertEqual(snapshot(samovar), before)

        errors = [
            ((0, "ground"), ValueError),
            ((NAN, "ground"), ValueError),
            ((INF, "sand"), ValueError),
            ((1, "lava"), ValueError),
            (("1", "ground"), TypeError),
            ((1, "air"), SamovarCannotFly),
            ((2, "water"), SamovarWouldSink),
        ]
        for args, exc in errors:
            with self.subTest(args=args):
                with self.assertRaises(exc):
                    samovar.calculate_steam(*args)
                self.assertEqual(snapshot(samovar), before)


class TestObstacles(unittest.TestCase):

    def test_tc14_overcome_success(self):
        """TC-14: успешное преодоление препятствий, включая граничные габариты."""
        # samovar params, obstacle, расход пара
        cases = [
            ({}, "ditch", 5.0),
            ({}, "boulder", 10.0),
            ({}, "narrow_bridge", 2.0),
            ({"track_width_m": 1.0}, "ditch", 5.0),             # граница >= 1.0
            ({"track_width_m": 1.5}, "narrow_bridge", 2.0),     # граница <= 1.5
            ({"mass_kg": 1000.0}, "narrow_bridge", 2.0),        # граница <= 1000
        ]
        for params, obstacle, cost in cases:
            with self.subTest(params=params, obstacle=obstacle):
                # Arrange
                samovar = make_samovar(**params)
                samovar.move(1, "sand")  # steam 98, position 1, terrain sand

                # Act
                can = samovar.can_overcome(obstacle)
                result = samovar.overcome(obstacle)

                # Assert
                self.assertIs(can, True)
                self.assertIsNone(result)
                self.assertAlmostEqual(samovar.steam, 98.0 - cost, places=PLACES)
                self.assertAlmostEqual(samovar.position_km, 1.0, places=PLACES)
                self.assertEqual(samovar.terrain, "sand")

    def test_tc15_overcome_geometry_failures(self):
        """TC-15: препятствие не по габаритам -> False и доменное исключение, пар не тратится."""
        cases = [
            ({}, "wall", SamovarStuck),
            ({"track_width_m": 0.99}, "ditch", SamovarStuck),
            ({"track_width_m": 1.51}, "narrow_bridge", SamovarTooWide),
            ({"mass_kg": 1000.1}, "narrow_bridge", SamovarTooHeavy),
        ]
        for params, obstacle, exc in cases:
            with self.subTest(params=params, obstacle=obstacle):
                # Arrange
                samovar = make_samovar(**params)
                before = snapshot(samovar)

                # Act / Assert
                self.assertIs(samovar.can_overcome(obstacle), False)
                with self.assertRaises(exc):
                    samovar.overcome(obstacle)
                self.assertEqual(snapshot(samovar), before)

    def test_tc16_overcome_state_failures(self):
        """TC-16: мало пара или порваны гусеницы -> False и доменное исключение."""
        # Arrange: пара 9 < 10, нужных валуну
        weak = make_samovar(steam=9.0)
        before_weak = snapshot(weak)

        # Act / Assert
        self.assertIs(weak.can_overcome("boulder"), False)
        with self.assertRaises(SamovarNoSteam):
            weak.overcome("boulder")
        self.assertEqual(snapshot(weak), before_weak)

        # Arrange: гусеницы порваны
        broken = make_samovar()
        broken.damage_tracks()
        before_broken = snapshot(broken)
        for obstacle in ("ditch", "boulder", "narrow_bridge"):
            with self.subTest(obstacle=obstacle):
                self.assertIs(broken.can_overcome(obstacle), False)
                with self.assertRaises(SamovarTracksBroken):
                    broken.overcome(obstacle)
                self.assertEqual(snapshot(broken), before_broken)

    def test_tc17_unknown_obstacle_raises(self):
        """TC-17: неизвестное препятствие -> ValueError, не строка -> TypeError."""
        samovar = make_samovar()
        cases = [("tree", ValueError), ("", ValueError), (42, TypeError), (None, TypeError)]
        for obstacle, exc in cases:
            for method in (samovar.can_overcome, samovar.overcome):
                with self.subTest(obstacle=obstacle, method=method.__name__):
                    with self.assertRaises(exc):
                        method(obstacle)


class TestTracks(unittest.TestCase):

    def test_tc18_damage_and_repair_tracks(self):
        """TC-18: damage_tracks / repair_tracks: стоимость ремонта, повторы, нехватка пара."""
        # Arrange
        samovar = make_samovar(steam=50.0)

        # Act / Assert: поломка (повторная поломка — без ошибки)
        self.assertIsNone(samovar.damage_tracks())
        samovar.damage_tracks()
        self.assertIs(samovar.tracks_ok, False)

        # Act / Assert: ремонт стоит 20 пара
        self.assertIsNone(samovar.repair_tracks())
        self.assertIs(samovar.tracks_ok, True)
        self.assertAlmostEqual(samovar.steam, 30.0, places=PLACES)

        # Act / Assert: ремонт целых гусениц ничего не меняет
        samovar.repair_tracks()
        self.assertIs(samovar.tracks_ok, True)
        self.assertAlmostEqual(samovar.steam, 30.0, places=PLACES)

        # Arrange / Act / Assert: на ремонт не хватает пара (19 < 20)
        poor = make_samovar(steam=19.0)
        poor.damage_tracks()
        before = snapshot(poor)
        with self.assertRaises(SamovarNoSteam):
            poor.repair_tracks()
        self.assertEqual(snapshot(poor), before)


class TestTea(unittest.TestCase):

    def test_tc19_brew_tea(self):
        """TC-19: brew_tea тратит 3 пара на чашку, считает чашки, проверяет аргументы."""
        # Arrange
        samovar = make_samovar()

        # Act
        spent = samovar.brew_tea(5)

        # Assert
        self.assertIsInstance(spent, float)
        self.assertAlmostEqual(spent, 15.0, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 85.0, places=PLACES)
        self.assertEqual(samovar.cups_served, 5)

        # граница: 10 чашек допустимо
        samovar.brew_tea(10)
        self.assertEqual(samovar.cups_served, 15)
        self.assertAlmostEqual(samovar.steam, 55.0, places=PLACES)

        # некорректные аргументы
        for cups, exc in ((0, ValueError), (11, ValueError), (-1, ValueError),
                          (2.5, TypeError), (True, TypeError), ("3", TypeError)):
            with self.subTest(cups=cups):
                before = snapshot(samovar)
                with self.assertRaises(exc):
                    samovar.brew_tea(cups)
                self.assertEqual(snapshot(samovar), before)

        # нехватка пара: 4 чашки = 12 > 10
        weak = make_samovar(steam=10.0)
        before = snapshot(weak)
        with self.assertRaises(SamovarNoSteam):
            weak.brew_tea(4)
        self.assertEqual(snapshot(weak), before)


class TestRefuel(unittest.TestCase):

    def test_tc20_refuel(self):
        """TC-20: refuel пополняет пар, но не выше 100; при полном запасе без ошибки; проверяет аргументы."""
        # Arrange
        samovar = make_samovar(steam=20.0)

        # Act / Assert
        self.assertIsNone(samovar.refuel(50))
        self.assertAlmostEqual(samovar.steam, 70.0, places=PLACES)

        capped = make_samovar(steam=50.0)
        capped.refuel(1000)
        self.assertAlmostEqual(capped.steam, 100.0, places=PLACES)

        full = make_samovar(steam=100.0)
        before_full = snapshot(full)
        self.assertIsNone(full.refuel(5))
        self.assertEqual(snapshot(full), before_full)

        for amount, exc in ((0, ValueError), (-1, ValueError),
                            (NAN, ValueError), (INF, ValueError),
                            (-INF, ValueError), (HUGE_INT, ValueError),
                            ("10", TypeError), (True, TypeError), (None, TypeError)):
            with self.subTest(amount=shown(amount)):
                before = snapshot(samovar)
                with self.assertRaises(exc):
                    samovar.refuel(amount)
                self.assertEqual(snapshot(samovar), before)


class TestStatus(unittest.TestCase):

    def test_tc21_get_status(self):
        """TC-21: get_status возвращает снимок с заявленными ключами и значениями."""
        # Arrange
        samovar = make_samovar()
        samovar.move(5, "sand")
        samovar.brew_tea(2)

        # Act
        status = samovar.get_status()

        # Assert
        self.assertEqual(
            set(status),
            {"name", "steam", "position_km", "terrain",
             "tracks_ok", "cups_served", "track_width_m"},
        )
        self.assertEqual(status["name"], "Пыхтун")
        self.assertAlmostEqual(status["steam"], 84.0, places=PLACES)
        self.assertAlmostEqual(status["position_km"], 5.0, places=PLACES)
        self.assertEqual(status["terrain"], "sand")
        self.assertIs(status["tracks_ok"], True)
        self.assertEqual(status["cups_served"], 2)
        self.assertAlmostEqual(status["track_width_m"], 1.2, places=PLACES)

        # снимок: изменение словаря не меняет самовар
        status["steam"] = 0.0
        status["terrain"] = "air"
        self.assertAlmostEqual(samovar.steam, 84.0, places=PLACES)
        self.assertEqual(samovar.terrain, "sand")


class TestExceptions(unittest.TestCase):

    def test_tc22_exception_hierarchy(self):
        """TC-22: доменные исключения образуют заявленную иерархию."""
        self.assertTrue(issubclass(CrazyVehicleError, RuntimeError))
        self.assertTrue(issubclass(SamovarError, CrazyVehicleError))
        for exc in DOMAIN_EXCEPTIONS:
            with self.subTest(exc=exc.__name__):
                self.assertTrue(issubclass(exc, SamovarError))
                self.assertFalse(issubclass(exc, (ValueError, TypeError)))


# ---------------------------------------------------------------------------
# Сценарные тесты (GWT)
# ---------------------------------------------------------------------------

class TestScenarios(unittest.TestCase):

    def test_tc23_tea_party_on_stone_pass(self):
        """TC-23: сценарий «Чаепитие на Каменном перевале» (SPEC 4.2.1)."""
        # Given самовар «Пыхтун»: 800 кг, гусеницы 1.2 м, 20 км/ч, пар 100
        samovar = make_samovar()
        машинист = Машинист(samovar)

        # When машинист едет 10 км по дороге
        hours = машинист.ехать(10)
        # Then
        self.assertAlmostEqual(hours, 0.5, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 90.0, places=PLACES)
        self.assertAlmostEqual(samovar.position_km, 10.0, places=PLACES)

        # When машинист едет 5 км по песку
        hours = машинист.ехать_по_песку(5)
        # Then скорость падает вдвое
        self.assertAlmostEqual(hours, 0.5, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 80.0, places=PLACES)
        self.assertEqual(samovar.terrain, "sand")

        # When машинист перескакивает канаву
        self.assertIs(машинист.может("ditch"), True)
        машинист.перескочить_канаву()
        # Then
        self.assertAlmostEqual(samovar.steam, 75.0, places=PLACES)

        # When машинист сталкивает валун
        машинист.столкнуть_валун()
        # Then
        self.assertAlmostEqual(samovar.steam, 65.0, places=PLACES)

        # When машинист заваривает 5 чашек чая
        spent = машинист.заварить_чай(5)
        # Then
        self.assertAlmostEqual(spent, 15.0, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 50.0, places=PLACES)
        self.assertEqual(samovar.cups_served, 5)

        # When машинист штурмует отвесную стену
        self.assertIs(машинист.может("wall"), False)
        with self.assertRaises(SamovarStuck):
            машинист.штурмовать_стену()
        # Then пар не потрачен
        self.assertAlmostEqual(samovar.steam, 50.0, places=PLACES)

        # When машинист переходит ручей вброд 0.5 км
        hours = машинист.вброд(0.5)
        # Then
        self.assertAlmostEqual(hours, 0.1, places=PLACES)

        # Then итоговое состояние
        status = машинист.доложить()
        self.assertAlmostEqual(status["position_km"], 15.5, places=PLACES)
        self.assertAlmostEqual(status["steam"], 48.5, places=PLACES)
        self.assertEqual(status["terrain"], "water")
        self.assertEqual(status["cups_served"], 5)
        self.assertIs(status["tracks_ok"], True)

    def test_tc24_rockfall_in_copper_mine(self):
        """TC-24: сценарий «Камнепад в Медной шахте» (SPEC 4.2.2)."""
        # Given «Пыхтун» с паром 60 у входа в шахту
        samovar = make_samovar(steam=60.0)
        машинист = Машинист(samovar)
        камнепад = Камнепад()

        # When машинист бурит 5 км под землёй
        hours = машинист.бурить(5)
        # Then
        self.assertAlmostEqual(hours, 1.0, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 40.0, places=PLACES)
        self.assertEqual(samovar.terrain, "underground")

        # When на самовар обрушивается камнепад
        камнепад.обрушиться_на(samovar)
        # Then гусеницы порваны
        self.assertIs(samovar.tracks_ok, False)

        # When машинист пытается бурить дальше
        with self.assertRaises(SamovarTracksBroken):
            машинист.бурить(1)
        # Then позиция не меняется
        self.assertAlmostEqual(samovar.position_km, 5.0, places=PLACES)

        # When машинист пытается столкнуть валун
        self.assertIs(машинист.может("boulder"), False)
        with self.assertRaises(SamovarTracksBroken):
            машинист.столкнуть_валун()

        # When пока ждёт, машинист заваривает 2 чашки (стоя на месте можно)
        машинист.заварить_чай(2)
        # Then
        self.assertAlmostEqual(samovar.steam, 34.0, places=PLACES)

        # When машинист чинит гусеницы
        машинист.починить_гусеницы()
        # Then
        self.assertIs(samovar.tracks_ok, True)
        self.assertAlmostEqual(samovar.steam, 14.0, places=PLACES)

        # When машинист пытается бурить ещё 5 км (нужно 20 пара)
        with self.assertRaises(SamovarNoSteam):
            машинист.бурить(5)
        # Then состояние не меняется
        self.assertAlmostEqual(samovar.steam, 14.0, places=PLACES)
        self.assertAlmostEqual(samovar.position_km, 5.0, places=PLACES)

        # When машинист прикидывает расход на 3.5 км и бурит их
        self.assertAlmostEqual(машинист.прикинуть(3.5, "underground"), 14.0,
                               places=PLACES)
        hours = машинист.бурить(3.5)
        # Then пар кончился ровно в ноль
        self.assertAlmostEqual(hours, 0.7, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 0.0, places=PLACES)
        self.assertAlmostEqual(samovar.position_km, 8.5, places=PLACES)

        # When машинист хочет заварить ещё чашку
        with self.assertRaises(SamovarNoSteam):
            машинист.заварить_чай(1)

        # When машинист подбрасывает 30 единиц шишек и выезжает на поверхность 2 км
        машинист.подбросить_шишек(30)
        машинист.ехать(2)

        # Then итоговое состояние
        status = машинист.доложить()
        self.assertAlmostEqual(status["position_km"], 10.5, places=PLACES)
        self.assertAlmostEqual(status["steam"], 28.0, places=PLACES)
        self.assertEqual(status["terrain"], "ground")
        self.assertIs(status["tracks_ok"], True)
        self.assertEqual(status["cups_served"], 2)

    def test_tc25_crossing_rotten_swamp(self):
        """TC-25: сценарий «Переправа через Гнилое болото» (SPEC 4.2.3)."""
        # Given тяжёлый самовар «Бульбуль»: 1500 кг, гусеницы 1.4 м, 30 км/ч, пар 50
        samovar = make_samovar(name="Бульбуль", mass_kg=1500.0,
                               track_width_m=1.4, max_speed_kmh=30.0,
                               steam=50.0)
        машинист = Машинист(samovar)

        # When машинист едет 6 км по дороге
        hours = машинист.ехать(6)
        # Then
        self.assertAlmostEqual(hours, 0.2, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 44.0, places=PLACES)

        # When машинист пытается переехать узкий мост
        self.assertIs(машинист.может("narrow_bridge"), False)
        with self.assertRaises(SamovarTooHeavy):
            машинист.переехать_мост()
        # Then пар не потрачен
        self.assertAlmostEqual(samovar.steam, 44.0, places=PLACES)

        # When машинист прикидывает брод 2 км и всё равно пытается
        with self.assertRaises(SamovarWouldSink):
            машинист.прикинуть(2, "water")
        with self.assertRaises(SamovarWouldSink):
            машинист.вброд(2)
        # Then самовар остался на берегу
        self.assertAlmostEqual(samovar.position_km, 6.0, places=PLACES)
        self.assertEqual(samovar.terrain, "ground")

        # When машинист переходит вброд мелкое место 0.5 км
        hours = машинист.вброд(0.5)
        # Then скорость 7.5 км/ч
        self.assertAlmostEqual(hours, 0.5 / 7.5, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 42.5, places=PLACES)
        self.assertEqual(samovar.terrain, "water")

        # When машинист в отчаянии пытается взлететь
        with self.assertRaises(SamovarCannotFly):
            машинист.взлететь()
        # Then самовар всё ещё в воде
        self.assertEqual(samovar.terrain, "water")

        # When машинист перескакивает канаву на выезде
        self.assertIs(машинист.может("ditch"), True)
        машинист.перескочить_канаву()
        # Then
        self.assertAlmostEqual(samovar.steam, 37.5, places=PLACES)

        # When машинист едет 3 км по песку
        hours = машинист.ехать_по_песку(3)
        # Then
        self.assertAlmostEqual(hours, 0.2, places=PLACES)

        # Then итоговое состояние
        status = машинист.доложить()
        self.assertEqual(status["name"], "Бульбуль")
        self.assertAlmostEqual(status["position_km"], 9.5, places=PLACES)
        self.assertAlmostEqual(status["steam"], 31.5, places=PLACES)
        self.assertEqual(status["terrain"], "sand")

    def test_tc26_whistle_and_owl_ravine(self):
        """TC-26: сценарий «Свисток и Совиный овраг» (SPEC 4.2.4)."""
        # Given лёгкий самовар «Свисток»: 400 кг, гусеницы 0.9 м, 40 км/ч, пар 30
        samovar = make_samovar(name="Свисток", mass_kg=400.0,
                               track_width_m=0.9, max_speed_kmh=40.0,
                               steam=30.0)
        машинист = Машинист(samovar)

        # When машинист едет 10 км по дороге
        hours = машинист.ехать(10)
        # Then
        self.assertAlmostEqual(hours, 0.25, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 20.0, places=PLACES)

        # When машинист пытается перескочить канаву узкими гусеницами
        self.assertIs(машинист.может("ditch"), False)
        with self.assertRaises(SamovarStuck):
            машинист.перескочить_канаву()
        # Then пар не потрачен
        self.assertAlmostEqual(samovar.steam, 20.0, places=PLACES)

        # When машинист объезжает канаву по узкому мосту
        self.assertIs(машинист.может("narrow_bridge"), True)
        машинист.переехать_мост()
        # Then
        self.assertAlmostEqual(samovar.steam, 18.0, places=PLACES)

        # When машинист отмечает переправу шестью чашками чая
        spent = машинист.заварить_чай(6)
        # Then пар ушёл весь
        self.assertAlmostEqual(spent, 18.0, places=PLACES)
        self.assertAlmostEqual(samovar.steam, 0.0, places=PLACES)
        self.assertEqual(samovar.cups_served, 6)

        # When машинист пытается ехать дальше
        with self.assertRaises(SamovarNoSteam):
            машинист.ехать(1)
        # Then позиция не меняется
        self.assertAlmostEqual(samovar.position_km, 10.0, places=PLACES)

        # When машинист подбрасывает целый мешок шишек (1000)
        машинист.подбросить_шишек(1000)
        # Then пар не выше 100
        self.assertAlmostEqual(samovar.steam, 100.0, places=PLACES)

        # When машинист едет 20 км по песку
        hours = машинист.ехать_по_песку(20)
        # Then
        self.assertAlmostEqual(hours, 1.0, places=PLACES)

        # Then итоговое состояние
        status = машинист.доложить()
        self.assertAlmostEqual(status["position_km"], 30.0, places=PLACES)
        self.assertAlmostEqual(status["steam"], 60.0, places=PLACES)
        self.assertEqual(status["terrain"], "sand")
        self.assertEqual(status["cups_served"], 6)


if __name__ == "__main__":
    unittest.main()
