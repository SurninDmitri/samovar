# Test Case Specification: Гусеничный самовар «Пыхтун»

Автор: Игнатьева Мария Сергеевна\
Версия: 0.2 (к SPEC.md v0.2)\
Код тестов: `tests/test_tracked_samovar.py`

Ссылка на тест в артефактах (BUGREPORT, CHANGELOG, FIXES, REVIEW) идёт именно на ID из этих таблиц. Имя каждого тест-метода начинается с `test_tcNN_`, docstring начинается с `TC-NN`.

Эталонный самовар («Пыхтун»), если не сказано иное: `name="Пыхтун"`, `mass_kg=800`, `track_width_m=1.2`, `max_speed_kmh=20`, `steam=100`.

Соотношение: 22 модульных / 4 сценарных ≈ 85 / 15.

## Модульные тесты (AAA)

| ID | Тип | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|---|
| TC-01 | module | SPEC 3.0, 3.2, 3.3, 5 | — | `TrackedSamovar("Пыхтун", 800, 1.2, 20)`; также `steam=0`, `steam=100`; `mass_kg` — подкласс `float`, `max_speed_kmh` — подкласс `int` | параметры сохранены; `steam=100.0`, `position_km=0.0`, `terrain="ground"`, `tracks_ok=True`, `cups_served=0`; steam 0 и 100 допустимы; подклассы приняты, атрибуты имеют тип ровно `float` | high |
| TC-02 | module | SPEC 3.2 | — | `name=""`, `"   "`, `"\t\n"` | `ValueError` | high |
| TC-03 | module | SPEC 3.0, 3.2, 5 | — | `mass_kg` / `track_width_m` / `max_speed_kmh` = `0`, `0.0`, `-1.0`, `nan`, `inf`, `-inf`, `10**400` | `ValueError` | high |
| TC-04 | module | SPEC 3.0, 3.2, 5 | — | `steam=-0.1`, `100.1`, `1000`, `nan`, `inf`, `-inf` | `ValueError` | high |
| TC-05 | module | SPEC 3.2, 6.2 | — | `name=123`, `name=None`, `mass_kg="800"`, `track_width_m=None`, `max_speed_kmh=[20]`, `steam=True`, `mass_kg=False` | `TypeError` | medium |
| TC-06 | module | SPEC 3.3 | эталонный самовар | присваивание каждому публичному атрибуту | `AttributeError` | medium |
| TC-07 | module | SPEC 3.4.1, 4.1 (сц. 1) | эталонный самовар | `move(10,"ground")`, `move(5,"sand")`, `move(5,"underground")`, `move(0.5,"water")` | время 0.5 / 0.5 / 1.0 / 0.1 ч; steam 90 / 90 / 80 / 98.5; `position_km = distance`; `terrain` = переданная среда; результат `float` | high |
| TC-08 | module | SPEC 3.0, 3.4.1, 5, 6.2 | эталонный самовар | `move(0,"ground")`, `move(-5,"ground")`, `move(1,"lava")`, `move(1,"")`, `move(nan,"ground")`, `move(inf,"ground")`, `move(-inf,"ground")`, `move(10**400,"ground")`; `move("abc","ground")`, `move(True,"ground")`, `move(None,"ground")`, `move(1,1)` | `ValueError` ×8; `TypeError` ×4; состояние не меняется | high |
| TC-09 | module | SPEC 2, 3.4.1, 5 | эталонный самовар | `move(1,"air")`; `move(0.6,"water")`; `move(0.5000001,"water")` | `SamovarCannotFly`; `SamovarWouldSink` ×2; состояние не меняется | high |
| TC-10 | module | SPEC 3.4.1, 4.1 (сц. 2) | `steam=20` | `move(30,"ground")` | `SamovarNoSteam`; состояние не меняется | high |
| TC-11 | module | SPEC 3.4.1, 5 | `steam=20` | `move(20,"ground")` | возвращает 1.0; `steam=0.0`; `position_km=20` | high |
| TC-12 | module | SPEC 2, 3.4.1 | `damage_tracks()` | `move(0.5, t)` для `t` ∈ ground, sand, underground, water | `SamovarTracksBroken`; состояние не меняется | high |
| TC-13 | module | SPEC 3.0, 3.4.2 | `steam=0`, `damage_tracks()` | `calculate_steam(10,"ground")`, `(5,"sand")`, `(5,"underground")`, `(0.5,"water")`; ошибки: `(0,"ground")`, `(nan,"ground")`, `(inf,"sand")`, `(1,"lava")`, `("1","ground")`, `(1,"air")`, `(2,"water")` | 10 / 10 / 20 / 1.5 (`float`); `ValueError` ×4, `TypeError`, `SamovarCannotFly`, `SamovarWouldSink`; состояние не меняется | high |
| TC-14 | module | SPEC 3.4.3, 3.4.4, 4.1 (сц. 3), 5 | после `move(1,"sand")`: `steam=98`; варианты: эталон, `track_width_m=1.0`, `1.5`, `mass_kg=1000` | `can_overcome(o)`, затем `overcome(o)` для ditch / boulder / narrow_bridge | `True`; `None`; steam −5 / −10 / −2; `position_km=1`, `terrain="sand"` не меняются | high |
| TC-15 | module | SPEC 3.4.3, 3.4.4, 5 | эталон; `track_width_m=0.99`; `1.51`; `mass_kg=1000.1` | `"wall"`; `"ditch"`; `"narrow_bridge"`; `"narrow_bridge"` | `can_overcome` → `False`; `overcome` → `SamovarStuck`, `SamovarStuck`, `SamovarTooWide`, `SamovarTooHeavy`; состояние не меняется | high |
| TC-16 | module | SPEC 3.4.3, 3.4.4 | `steam=9`; отдельно — `damage_tracks()` | `"boulder"`; ditch / boulder / narrow_bridge | `False` + `SamovarNoSteam`; `False` + `SamovarTracksBroken`; состояние не меняется | high |
| TC-17 | module | SPEC 3.4.3, 3.4.4, 6.2 | эталонный самовар | `can_overcome` и `overcome` с `"tree"`, `""`, `42`, `None` | `ValueError`, `ValueError`, `TypeError`, `TypeError` | medium |
| TC-18 | module | SPEC 3.4.5, 3.4.6, 5 | `steam=50`; отдельно `steam=19` + `damage_tracks()` | `damage_tracks()` ×2, `repair_tracks()` ×2; `repair_tracks()` при `steam=19` | `tracks_ok=False` → `True`, `steam=30`, повторный ремонт ничего не меняет; `SamovarNoSteam`, гусеницы остаются порванными | high |
| TC-19 | module | SPEC 3.4.7, 5 | эталон; отдельно `steam=10` | `brew_tea(5)`, `brew_tea(10)`; `brew_tea(0/11/-1)`; `brew_tea(2.5/True/"3")`; `brew_tea(4)` при `steam=10` | 15.0 (`float`), steam 85 → 55, cups 5 → 15; `ValueError`; `TypeError`; `SamovarNoSteam`; при ошибке состояние не меняется | high |
| TC-20 | module | SPEC 3.0, 3.4.8, 4.1 (сц. 4), 5 | `steam=20`; `steam=50`; `steam=100` | `refuel(50)`; `refuel(1000)`; `refuel(5)` при полном запасе; `refuel(0/-1/nan/inf/-inf/10**400)`; `refuel("10"/True/None)` | `None`, steam 70; steam 100; без исключения, состояние не меняется; `ValueError`; `TypeError` | high |
| TC-21 | module | SPEC 3.4.9 | эталон, `move(5,"sand")`, `brew_tea(2)` | `get_status()`; изменение словаря | ключи ровно name, steam, position_km, terrain, tracks_ok, cups_served, track_width_m; значения "Пыхтун", 84, 5, "sand", True, 2, 1.2; самовар не меняется | high |
| TC-22 | module | SPEC 6.1 | — | классы исключений | `CrazyVehicleError ⊂ RuntimeError`; `SamovarError ⊂ CrazyVehicleError`; все 7 доменных ⊂ `SamovarError` и не ⊂ `ValueError`/`TypeError` | medium |

## Сценарные тесты (GWT)

| ID | Тип | Источник | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|
| TC-23 | scenario | SPEC 4.2.1 | шаги сценария «Чаепитие на Каменном перевале» (эталонный самовар) | `position_km=15.5`, `steam=48.5`, `terrain="water"`, `cups_served=5`, `tracks_ok=True` | high |
| TC-24 | scenario | SPEC 4.2.2 | шаги сценария «Камнепад в Медной шахте» (эталон, `steam=60`) | `position_km=10.5`, `steam=28`, `terrain="ground"`, `tracks_ok=True`, `cups_served=2` | high |
| TC-25 | scenario | SPEC 4.2.3 | шаги сценария «Переправа через Гнилое болото» («Бульбуль»: 1500 кг, 1.4 м, 30 км/ч, пар 50) | `position_km=9.5`, `steam=31.5`, `terrain="sand"` | high |
| TC-26 | scenario | SPEC 4.2.4 | шаги сценария «Свисток и Совиный овраг» («Свисток»: 400 кг, 0.9 м, 40 км/ч, пар 30) | `position_km=30`, `steam=60`, `terrain="sand"`, `cups_served=6` | medium |
