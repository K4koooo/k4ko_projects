# Door Defects Chatbot 🚪

Lokalny chatbot RAG (Retrieval-Augmented Generation) do analizy wad produkcyjnych drzwi.
Działa **w pełni offline** — żadne dane nie opuszczają Twojego komputera.

## Stos technologiczny

| Komponent | Technologia |
|---|---|
| LLM | Ollama (`SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M` lub `llama3.1:8b`) |
| Embeddingi | `nomic-embed-text` przez Ollama |
| Baza wektorowa | ChromaDB (persistent) |
| Backend | Python 3.11 + FastAPI + LangChain |
| Frontend | Next.js 14 + TypeScript + Material Design 3 |
| Orkiestracja | Docker Compose |

## Wymagania

- Docker Desktop (Windows/Mac/Linux) ≥ 24.0
- Minimum **16 GB RAM** (model Bielik 11B) lub **8 GB RAM** (llama3.1:8b)
- Minimum **20 GB wolnego miejsca** na dysku (modele Ollama)
- GPU NVIDIA opcjonalnie (CUDA) — bez GPU działa wolniej na CPU

## Pierwsze uruchomienie

```bash
# 1. Sklonuj / pobierz projekt
cd door-defects-chatbot

# 2. Skopiuj i skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env jeśli chcesz zmienić model lub inne parametry

# 3. Uruchom całość
docker compose up --build

# Pierwsze uruchomienie:
# - Pobierze model Bielik (~7 GB) lub llama3.1 (~5 GB) — jednorazowo
# - Pobierze model nomic-embed-text (~274 MB) — jednorazowo
# - Zaindeksuje pliki Excel z data/excel/
# - Uruchomi frontend pod http://localhost:3000

# 4. Otwórz przeglądarkę
start http://localhost:3000
```

## Dodawanie plików Excel

1. Wrzuć pliki `.xlsx` do folderu `data/excel/`
2. Kliknij **menu (☰) → Przeładuj dane Excel** w aplikacji
3. Lub użyj API: `curl -X POST http://localhost:8080/ingest`

Każdy wiersz Excela staje się osobnym dokumentem w bazie wektorowej.
Indeksowanie jest **idempotentne** — ponowne wrzucenie tego samego pliku nie duplikuje danych.

## Zmiana modelu LLM

Edytuj `.env`:

```bash
# Pełny model polski (zalecany, ~7 GB, wymaga ~8 GB VRAM lub ~16 GB RAM)
LLM_MODEL=SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M

# Fallback dla słabszego sprzętu (~5 GB)
LLM_MODEL=llama3.1:8b

# Mały i szybki (angielski, ~2 GB)
LLM_MODEL=llama3.2:3b
```

Następnie zrestartuj backend:
```bash
docker compose restart backend
```

## Customizacja kolorów (Material Design 3)

Kolor główny (seed) to `#0B57D0` (Google Blue). Aby zmienić:

1. Edytuj `frontend/app/globals.css` — sekcje `:root` (jasny) i `[data-theme='dark']`
2. Edytuj `frontend/lib/theme.ts` — obiekty `lightTokens` i `darkTokens`
3. Użyj [Material Theme Builder](https://m3.material.io/theme-builder) aby wygenerować nową paletę

## API backendu

```
POST /chat          Streaming SSE chat z RAG
POST /ingest        Re-indeksuj pliki Excel
GET  /health        Status Ollama, ChromaDB i modeli
GET  /stats         Statystyki bazy (liczba dokumentów, pliki)
```

### Przykład `/chat`:
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Jakie są najczęstsze wady powierzchni?", "top_k": 5}' \
  --no-buffer
```

## Porty

| Serwis | Port |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8080 |
| ChromaDB | http://localhost:8001 |
| Ollama | http://localhost:11434 |

## Skróty klawiszowe

| Skrót | Akcja |
|---|---|
| `Enter` | Wyślij wiadomość |
| `Shift+Enter` | Nowa linia |
| `Ctrl/Cmd+K` | Nowy czat |
| `Esc` | Zamknij menu |

## Troubleshooting

### Backend nie startuje
```bash
# Sprawdź logi
docker compose logs backend

# Sprawdź czy Ollama odpowiada
curl http://localhost:11434/api/tags
```

### "Nie znalazłem tej informacji"
- Sprawdź czy pliki .xlsx są w `data/excel/`
- Kliknij **Przeładuj dane Excel** w menu
- Sprawdź statystyki: `curl http://localhost:8080/stats`

### Bardzo wolne odpowiedzi
- Bez GPU model działa na CPU — to normalne (kilkadziesiąt sekund)
- Użyj mniejszego modelu: `LLM_MODEL=llama3.2:3b` w `.env`

### Reset bazy ChromaDB
```bash
docker compose down
docker volume rm door-defects-chatbot_chroma_data
docker compose up
```

### Zatrzymanie i usunięcie wszystkiego
```bash
docker compose down -v  # -v usuwa też woluminy (dane Ollama, Chroma)
```

## Struktura projektu

```
door-defects-chatbot/
├── docker-compose.yml
├── .env.example
├── data/excel/          ← tutaj wrzucasz pliki .xlsx
├── backend/
│   └── app/
│       ├── config.py    ← konfiguracja
│       ├── ingest.py    ← parsowanie Excel → ChromaDB
│       ├── rag.py       ← pipeline RAG ze streamingiem
│       └── main.py      ← FastAPI endpoints
└── frontend/
    ├── app/             ← Next.js App Router
    ├── components/      ← komponenty UI (Material Design 3)
    └── lib/             ← API client, typy, theme
```
