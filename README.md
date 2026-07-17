# Kalkulator z interfejsem graficznym

Lekka aplikacja desktopowa napisana w Pythonie i Tkinterze. Nie wymaga zewnętrznych bibliotek do uruchomienia.

## Funkcje

- dodawanie, odejmowanie, mnożenie i dzielenie;
- liczby dziesiętne, procenty i zmiana znaku;
- kasowanie ostatniego znaku oraz pełne czyszczenie;
- obsługa klawiatury;
- czytelny, responsywny interfejs;
- bezpieczna obsługa dzielenia przez zero;
- oddzielony silnik obliczeń objęty testami.

## Uruchomienie

```powershell
python calculator.py
```

## Testy

```powershell
python -m pip install pytest
python -m pytest -q
```

## Skróty klawiaturowe

- `0–9`, `+`, `-`, `*`, `/` — wprowadzanie działań;
- `Enter` lub `=` — wynik;
- `Backspace` — usuń ostatni znak;
- `Escape` lub `Delete` — wyczyść;
- `.` lub `,` — separator dziesiętny.
