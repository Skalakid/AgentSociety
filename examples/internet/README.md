# Internet Simulation - Przykład AgentSociety

## Opis

Ten przykład demonstruje symulację agentów z dostępem do internetu i urządzeń ICT (technologie informacyjno-komunikacyjne). Agenci są wyposażeni w różne urządzenia (smartfony, laptopy, desktopy, tablety) i mogą korzystać z internetu do przeglądania stron, mediów społecznościowych, zakupów online i innych aktywności.

### Główne cechy:

- **Urządzenia ICT**: Agenci posiadają różne urządzenia w zależności od wieku, zawodu i innych cech demograficznych
- **Świadomość internetu**: Agenci wiedzą, czy mają dostęp do internetu i jakie urządzenia posiadają
- **Anteny komórkowe**: Symulacja zasięgu sieci komórkowej na podstawie lokalizacji anten
- **Strony internetowe**: Baza danych stron WWW, z których agenci mogą korzystać

## Wymagania

- Python 3.8+
- Biblioteka `agentsociety` zainstalowana w środowisku Python

## Instalacja

### 1. Utworzenie środowiska wirtualnego (zalecane)

```bash
# Stwórz nowe środowisko wirtualne
python -m venv venv

# Aktywuj środowisko wirtualne
# Na macOS/Linux:
source venv/bin/activate
# Na Windows:
# venv\Scripts\activate
```

### 2. Instalacja biblioteki agentsociety

Z głównego katalogu projektu `agentsociety`:

```bash
pip install agentsociety
```

## Jak uruchomić

### 1. Konfiguracja API Key

Otwórz plik `internet.py` i znajdź sekcję konfiguracji LLM (około linii 30):

```python
llm=[
    LLMConfig(
        provider=LLMProviderType.ZhipuAI,
        base_url=None,
        api_key="TUTAJ_WPISZ_SWOJ_KLUCZ_API",  # <-- Zmień to!
        model="GLM-4-Flash",
        semaphore=200,
    )
]
```

**Zamień wartość `api_key`** na swój klucz API od dostawcy LLM (np. ZhipuAI, OpenAI, lub inny skonfigurowany w systemie).

### 2. Uruchomienie symulacji

Z katalogu `examples/internet` wykonaj:

```bash
python internet.py
```

### 3. Parametry symulacji

W pliku `internet.py` możesz dostosować:

- **Liczbę agentów**: `number=100` (domyślnie 100 agentów)
- **Czas symulacji**: `total_tick=8*60*60` (domyślnie 8 godzin)
- **Godzina startu**: `start_tick=12*60*60` (domyślnie 12:00)
- **Nazwa eksperymentu**: `name="internet 11.12 device test"`

## Wyniki symulacji

Po uruchomieniu symulacji wyniki będą zapisane w następujących lokalizacjach:

### 1. Logi symulacji - folder `internet_logs/`

Folder z szczegółowymi logami w formacie JSONL (JSON Lines) - każda linia to osobny obiekt JSON:

#### `device_usage_logs.jsonl`

Zawiera szczegółowe informacje o tym, jak agenci używają swoich urządzeń ICT:

- **timestamp** - dokładny czas akcji
- **agent_id, agent_name** - identyfikator i nazwa agenta
- **device_id, device_type, device_name** - informacje o użytym urządzeniu (smartphone, laptop, desktop, tablet)
- **action_type** - typ akcji (np. "work", "browse", "shop", "social", "search")
- **action_description** - szczegółowy opis tego, co agent zrobił
- **task_target** - cel zadania, które agent próbuje osiągnąć
- **success** - czy akcja zakończyła się sukcesem
- **metadata** - dodatkowe informacje (typ kroku, indeks planu, cel nadrzędny)

Przykład:

```json
{
  "timestamp": "2025-12-11T21:38:39.648754",
  "agent_id": 50,
  "agent_name": "InternetAgent_50",
  "device_id": "50_smartphone",
  "device_type": "smartphone",
  "device_name": "Smartphone",
  "action_type": "work",
  "action_description": "Log in to work email and check for tasks",
  "task_target": "Begin working from home",
  "success": true,
  "metadata": { "step_type": "other", "step_index": 0, "plan_target": "Work" }
}
```

#### `antenna_device_connections.jsonl`

Rejestruje połączenia urządzeń z antenami komórkowymi:

- **timestamp** - czas połączenia/rozłączenia
- **action** - "connect" lub "disconnect"
- **antenna_id** - identyfikator anteny
- **antenna_position** - pozycja anteny (x, y)
- **agent_id, agent_name** - identyfikator i nazwa agenta
- **device_id, device_type, device_name** - informacje o urządzeniu
- **ip_address** - przydzielony adres IP (przy połączeniu)

Przykład:

```json
{
  "timestamp": "2025-12-11T20:23:07.300395",
  "action": "connect",
  "antenna_id": 41,
  "antenna_position": { "x": -2500.0, "y": -2500.0 },
  "agent_id": 16,
  "agent_name": "InternetAgent_16",
  "device_name": "Smartphone",
  "device_type": "smartphone",
  "device_id": "16_smartphone",
  "ip_address": "10.0.41.67"
}
```

### 2. Katalog logów systemowych

- **`log/`** (w głównym katalogu projektu) - zawiera skompresowane logi z każdego uruchomienia
- Foldery nazwane według daty i godziny uruchomienia (format: `RRRRMMDD-GGMMSS-agentsociety`)

## Pliki konfiguracyjne

- **`internet.py`** - główny plik uruchamiający symulację z konfiguracją
- **`internetagent.py`** - definicja agenta z obsługą urządzeń ICT
- **`internet_memory_config.py`** - konfiguracja pamięci agenta z polami dla urządzeń ICT
- **`utils/ict_devices.py`** - logika przypisywania urządzeń i zarządzania nimi
- **`utils/antennas.py`** - dane o lokalizacjach anten komórkowych
- **`utils/websites.py`** - baza danych stron internetowych
- **`profiles_with_aoi.json`** - profile agentów z obszarami zainteresowań
