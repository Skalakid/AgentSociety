MIN_X = -20000.0  # Minimalna współrzędna X mapy
MAX_X = 20000.0   # Maksymalna współrzędna X mapy
MIN_Y = -20000.0  # Minimalna współrzędna Y mapy
MAX_Y = 20000.0   # Maksymalna współrzędna Y mapy

ANTENNA_RANGE = 5000.0

def _generate_antennas_grid(min_x, max_x, min_y, max_y, antenna_range):
    """
    Generuje listę anten rozmieszczonych równomiernie w siatce,
    tak aby pokryć cały zadany obszar.
    Ta funkcja jest wywoływana tylko raz podczas ładowania modułu.
    """
    antennas = []
    antenna_id_counter = 1

    # Odległość między środkami anten w siatce.
    # Wartość 1.5 * antenna_range zapewnia odpowiednie pokrycie i nakładanie.
    step_x = antenna_range * 1.5
    step_y = antenna_range * 1.5

    # Obliczanie punktu startowego, aby zasięg pierwszej anteny obejmował początek mapy.
    start_x = min_x - (antenna_range / 2)
    start_y = min_y - (antenna_range / 2)

    current_x = start_x
    while current_x <= max_x + (antenna_range / 2):
        current_y = start_y
        while current_y <= max_y + (antenna_range / 2):
            antennas.append({
                "id": antenna_id_counter,
                "category": "antenna",
                "position": {"x": current_x, "y": current_y},
                "range": antenna_range # Dodajemy zasięg do obiektu anteny
            })
            antenna_id_counter += 1
            current_y += step_y
        current_x += step_x
    
    return antennas

ANTENNAS = _generate_antennas_grid(MIN_X, MAX_X, MIN_Y, MAX_Y, ANTENNA_RANGE)

print(f"[{__name__}] Wygenerowano {len(ANTENNAS)} anten pokrywających mapę.")