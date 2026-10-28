from tracked_samovar import (
    TrackedSamovar,
    SamovarCannotFly,
    SamovarWouldSink,
    SamovarTracksBroken,
    SamovarNoSteam,
    SamovarStuck,
)


def print_status(title: str, samovar: TrackedSamovar):
    print(f"\n========== [{title}] ==========")
    status = samovar.get_status()
    print(f"Статус самовара '{status['name']}':")
    print(f"  - Позиция: {status['position_km']} км | Среда: {status['terrain']}")
    print(
        f"  - Запас пара: {status['steam']} ед. | Гусеницы исправны: {status['tracks_ok']}"
    )
    print(
        f"  - Чашек чая заварено: {status['cups_served']}"
        f" | Ширина гусениц: {status['track_width_m']} м"
    )


def run_demo():
    print("🚀 Запуск демонстрации проекта: Гусеничный самовар «Пыхтун»\n")

    # 1. Инициализация
    pyhtun = TrackedSamovar(
        name="Пыхтун", mass_kg=800.0, track_width_m=1.2, max_speed_kmh=20.0, steam=100.0
    )
    print_status("1. Инициализация самовара", pyhtun)

    # 2. Обычная поездка по дороге
    time_spent = pyhtun.move(10.0, "ground")
    print(f"\n-> Проехали 10 км по дороге. Затрачено времени: {time_spent} ч.")
    print_status("2. После поездки по дороге", pyhtun)

    # 3. Поездка по песку
    pyhtun.move(5.0, "sand")
    print("\n-> Проехали 5 км по песку (скорость упала вдвое, расход х2).")
    print_status("3. После поездки по песку", pyhtun)

    # 4. Препятствия
    print("\n--- Проверка препятствий ---")
    print(f"Можно перескочить канаву ('ditch')? {pyhtun.can_overcome('ditch')}")
    pyhtun.overcome("ditch")
    print("-> Перескочили канаву (-5 пара).")

    pyhtun.overcome("boulder")
    print("-> Столкнули валун (-10 пара).")
    print_status("4. После преодоления канавы и валуна", pyhtun)

    # 5. Исключения стихии
    print("\n--- Демонстрация ограничений и исключений стихии ---")
    try:
        pyhtun.overcome("wall")
    except SamovarStuck as e:
        print(f"[Поймано исключение] Стену штурмовать нельзя: {e}")

    try:
        pyhtun.move(1.0, "air")
    except SamovarCannotFly as e:
        print(f"[Поймано исключение] Самовар не летает: {e}")

    try:
        pyhtun.move(1.0, "water")
    except SamovarWouldSink as e:
        print(f"[Поймано исключение] Брод длиннее 0.5 км — утонем: {e}")

    pyhtun.move(0.5, "water")
    print("-> Успешно перешли мелкий ручей вброд (0.5 км).")
    print_status("5. После перехода ручья", pyhtun)

    # 6. Чай и заправка
    spent_steam = pyhtun.brew_tea(4)
    print(f"\n-> Заварили 4 чашки чая, израсходовано пара: {spent_steam}")

    pyhtun.refuel(40.0)
    print("-> Подбросили шишек (+40 пара).")
    print_status("6. Чаепитие и заправка", pyhtun)

    # 7. Предварительный расчет
    est_steam = pyhtun.calculate_steam(8.0, "ground")
    print(
        f"\n-> Предварительный расчёт пара на 8 км по дороге: "
        f"{est_steam} ед. (состояние не изменилось)"
    )

    # 8. Камнепад и ремонт
    print("\n--- Чрезвычайная ситуация: Камнепад ---")
    pyhtun.damage_tracks()
    print("-> Обрушился камнепад! Гусеницы повреждены.")

    try:
        pyhtun.move(2.0, "ground")
    except SamovarTracksBroken as e:
        print(f"[Поймано исключение] Нельзя ехать с порванными гусеницами: {e}")

    try:
        pyhtun.overcome("boulder")
    except SamovarTracksBroken as e:
        print(
            f"[Поймано исключение] Преодолевать препятствия с порванными гусеницами нельзя: {e}"
        )

    pyhtun.repair_tracks()
    print("-> Машинист починил гусеницы (-20 пара). Гусеницы снова исправны!")
    print_status("7. После починки гусениц", pyhtun)

    # 9. Подземный режим и нехватка пара
    print("\n--- Уходим под землю ---")
    try:
        pyhtun.move(100.0, "ground")
    except SamovarNoSteam as e:
        print(f"[Поймано исключение] Не хватило пара на дальнюю поездку: {e}")

    pyhtun.refuel(50.0)
    pyhtun.move(4.0, "underground")
    print("-> Пробурили 4 км под землей (высокий расход: 4 ед. на 1 км).")
    print_status("8. Финальное состояние самовара", pyhtun)

    print("\n🎉 Демонстрация успешно завершена!")


if __name__ == "__main__":
    run_demo()
