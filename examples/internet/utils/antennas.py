import math
import datetime
import json
import os
import threading
import random
from typing import Optional, Tuple

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
        self.active_connections = set()  # Set of agent IDs currently connected

    def is_within_range(self, agent_position: dict) -> bool:
        """
        Sprawdza, czy dana pozycja agenta znajduje się w zasięgu anteny.
        """
        distance = math.sqrt(
            (self.position['x'] - agent_position['x'])**2 +
            (self.position['y'] - agent_position['y'])**2
        )
        return distance <= self.range

    def surf_internet(self, agent_id: int, agent_name: str, interests: dict, known_websites: list) -> Tuple[Optional[str], int]:
        """
        Jedyna metoda dostępu do internetu dla agentów. Wybiera stronę na podstawie zainteresowań
        i znanych stron, zapisuje log aktywności i zwraca wybraną stronę wraz z czasem przeglądania.

        Args:
            agent_id (int): ID agenta
            agent_name (str): Nazwa agenta
            interests (dict): Słownik zainteresowań agenta
            known_websites (list): Lista znanych stron agenta

        Returns:
            Tuple[Optional[str], int]: (wybrana strona, czas przeglądania w tickach)
        """
        if agent_id not in self.active_connections:
            return None, 0

        # Wybierz stronę na podstawie zainteresowań i znanych stron
        website = self._select_website(interests, known_websites)
        if not website:
            return None, 0

        # Określ czas przeglądania (5-15 minut)
        duration = random.randint(300, 900)

        # Zapisz log aktywności
        self._log_activity(agent_id, agent_name, website, duration)

        return website, duration

    def _select_website(self, interests: dict, known_websites: list) -> Optional[str]:
        """
        Wybiera stronę na podstawie zainteresowań i znanych stron.
        """
        # Najpierw spróbuj wybrać ze znanych stron o wysokiej ocenie
        high_score_sites = [site for site in known_websites if site["score"] >= 7]
        if high_score_sites:
            return random.choice(high_score_sites)["website"]

        # Jeśli nie ma stron o wysokiej ocenie, wybierz na podstawie zainteresowań
        interest_weights = {k: v/10 for k, v in interests.items()}
        selected_interest = random.choices(
            list(interest_weights.keys()),
            weights=list(interest_weights.values()),
            k=1
        )[0]

        # Pobierz dostępne strony dla wybranego zainteresowania
        available_sites = WEBSITE_DATABASE.get(selected_interest, [])
        if available_sites:
            return random.choice(available_sites)

        return None

    def _log_activity(self, agent_id: int, agent_name: str, website_url: str, duration_ticks: int):
        """
        Zapisuje log aktywności internetowej do pliku.
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "antenna_id": self.id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "website_url": website_url,
            "duration_ticks": duration_ticks
        }
        
        with log_file_lock:
            with open(FULL_GLOBAL_LOG_PATH, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

    def connect_agent(self, agent_id: int):
        """Dodaje agenta do listy aktywnych połączeń"""
        self.active_connections.add(agent_id)

    def disconnect_agent(self, agent_id: int):
        """Usuwa agenta z listy aktywnych połączeń"""
        self.active_connections.discard(agent_id)

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