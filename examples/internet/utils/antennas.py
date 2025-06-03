import math
import datetime
import json
import os
import threading # Dodajemy threading dla zabezpieczenia przed race condition przy zapisie

MIN_X = -30000.0  # Minimalna współrzędna X mapy
MAX_X = 30000.0   # Maksymalna współrzędna X mapy
MIN_Y = -30000.0  # Minimalna współrzędna Y mapy
MAX_Y = 30000.0   # Maksymalna współrzędna Y mapy

ANTENNA_RANGE = 5000.0

# --- Globalna ścieżka do pliku logu internetowego ---
# Możesz zmienić nazwę pliku, jeśli chcesz
GLOBAL_INTERNET_LOG_FILE = "all_internet_activity_logs.jsonl"
# Możesz także zdefiniować katalog logów, jeśli chcesz
GLOBAL_LOG_DIR = "internet_logs"

# Zapewniamy, że katalog logów istnieje
os.makedirs(GLOBAL_LOG_DIR, exist_ok=True)
# Pełna ścieżka do pliku logu
FULL_GLOBAL_LOG_PATH = os.path.join(GLOBAL_LOG_DIR, GLOBAL_INTERNET_LOG_FILE)

# Tworzymy blokadę (lock) do bezpiecznego zapisu do pliku,
# aby uniknąć problemów, gdy wiele anten próbuje zapisać jednocześnie.
log_file_lock = threading.Lock()

class Antenna:
    """
    Reprezentuje pojedynczą antenę w symulacji, odpowiedzialną za
    obsługę połączeń internetowych i zapisywanie logów aktywności
    do wspólnego pliku.
    """

    def __init__(self, id: int, position: dict, range: float):
        """
        Inicjalizuje obiekt Antena.

        Args:
            id (int): Unikalny identyfikator anteny.
            position (dict): Słownik z kluczami 'x' i 'y' reprezentujący pozycję anteny.
            range (float): Zasięg działania anteny w metrach.
        """
        self.id = id
        self.category = "antenna"
        self.position = position
        self.range = range

    def is_within_range(self, agent_position: dict) -> bool:
        """
        Sprawdza, czy dana pozycja agenta znajduje się w zasięgu anteny.
        """
        distance = math.sqrt(
            (self.position['x'] - agent_position['x'])**2 +
            (self.position['y'] - agent_position['y'])**2
        )
        return distance <= self.range

    def log_internet_activity(self, agent_id: int, agent_name: str, website_url: str, duration_ticks: int):
        """
        Zapisuje log aktywności internetowej do jednego wspólnego pliku JSONL.
        Używa blokady, aby zapewnić bezpieczeństwo zapisu współbieżnego.
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "antenna_id": self.id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "website_url": website_url,
            "duration_ticks": duration_ticks
        }
        
        # Używamy blokady, aby tylko jedna antena mogła zapisywać do pliku w danym momencie
        with log_file_lock:
            with open(FULL_GLOBAL_LOG_PATH, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

    def to_dict(self):
        """Zwraca reprezentację anteny w formie słownika."""
        return {
            "id": self.id,
            "category": self.category,
            "position": self.position,
            "range": self.range
        }

def _generate_antennas_grid(min_x, max_x, min_y, max_y, antenna_range):
    """
    Generuje listę obiektów Antenna rozmieszczonych równomiernie w siatce,
    tak aby pokryć cały zadany obszar.
    """
    antennas = []
    antenna_id_counter = 1

    step_x = antenna_range * 1.5
    step_y = antenna_range * 1.5

    start_x = min_x - (antenna_range / 2)
    start_y = min_y - (antenna_range / 2)

    current_x = start_x
    while current_x <= max_x + (antenna_range / 2):
        current_y = start_y
        while current_y <= max_y + (antenna_range / 2):
            antennas.append(
                Antenna(
                    id=antenna_id_counter,
                    position={"x": current_x, "y": current_y},
                    range=antenna_range
                )
            )
            antenna_id_counter += 1
            current_y += step_y
        current_x += step_x
    
    return antennas

# Globalna lista anten, zawierająca obiekty Antenna
ANTENNAS = _generate_antennas_grid(MIN_X, MAX_X, MIN_Y, MAX_Y, ANTENNA_RANGE)

print(f"[{__name__}] Wygenerowano {len(ANTENNAS)} obiektów Antena pokrywających mapę.")

print(ANTENNAS[0].to_dict())  # Przykładowe wyświetlenie pierwszej anteny