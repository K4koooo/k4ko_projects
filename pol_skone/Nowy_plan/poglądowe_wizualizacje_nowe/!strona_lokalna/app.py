from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import shutil
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from czyszczenie_wad import transformuj_raport
import httpx
import pandas as pd

app = FastAPI(title="Pol-Skone Analiza Wad")

# Pula wątków do operacji blokujących (I/O plik, pandas)
executor = ThreadPoolExecutor(max_workers=4)

# Utworzenie folderu na tymczasowe pliki jeśli nie istnieje
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Konfiguracja plików statycznych i szablonów
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Domyślny URL dla lokalnej instancji Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Aktywny plik kontekstu (aktualizowany po każdym przetworzeniu)
active_processed_file: str = ""


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.post("/api/process-file")
async def process_file(file: UploadFile = File(...)):
    global active_processed_file
    try:
        # Zapisz plik lokalnie
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Wywołaj skrypt czyszczący w osobnym wątku (operacja blokująca)
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}_forPowerFI.xlsx"
        output_path = os.path.join(UPLOAD_DIR, output_filename)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, transformuj_raport, file_location, output_path
        )

        if result.get("success"):
            active_processed_file = output_filename
            return {
                "success": True,
                "message": f"Znaleziono {result['records_count']} unikalnych zgłoszeń. Plik gotowy do pobrania.",
                "download_url": f"/api/download/{output_filename}",
                "processed_filename": output_filename
            }
        else:
            return {"success": False, "error": result.get("error", "Nieznany błąd podczas przetwarzania.")}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/current-file")
async def get_current_file():
    """
    Zwraca nazwę ostatnio przetworzonego pliku.
    Najpierw sprawdza pamięć serwera, potem folder uploads (po dacie modyfikacji).
    """
    # 1) Użyj zapamiętanego pliku z bieżącej sesji
    if active_processed_file:
        path = os.path.join(UPLOAD_DIR, active_processed_file)
        if os.path.exists(path):
            return {"filename": active_processed_file}

    # 2) Fallback — znajdź najnowszy plik _forPowerFI.xlsx w uploads
    try:
        pliki = [
            f for f in os.listdir(UPLOAD_DIR)
            if f.endswith("_forPowerFI.xlsx")
        ]
        if pliki:
            najnowszy = max(
                pliki,
                key=lambda f: os.path.getmtime(os.path.join(UPLOAD_DIR, f))
            )
            return {"filename": najnowszy}
    except Exception:
        pass

    return {"filename": ""}


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    return {"error": "Plik nie istnieje."}


def _wczytaj_excel_sync(file_path: str) -> str:
    """Synchroniczne czytanie Excel — uruchamiane w osobnym wątku."""
    try:
        df = pd.read_excel(file_path)
        # Ogranicz do max 80 wierszy — mały model ma mały kontekst
        df_preview = df.head(80).fillna("")

        # Podsumowanie statystyczne zamiast surowych danych
        kolumny = list(df_preview.columns)
        n_total = len(df)
        n_preview = len(df_preview)

        # Nagłówek z listą kolumn
        naglowek = f"Plik zawiera {n_total} wierszy i {len(kolumny)} kolumn.\nKolumny: {', '.join(str(c) for c in kolumny)}\n\n"

        # Dane jako tabela tekstowa (pipe-separated)
        wiersze = []
        for _, row in df_preview.iterrows():
            wiersze.append(" | ".join(str(v) for v in row.values))

        tabela = f"Dane (pierwsze {n_preview} z {n_total} wierszy):\n{' | '.join(str(c) for c in kolumny)}\n" + "\n".join(wiersze)

        return naglowek + tabela
    except Exception as e:
        return f"[Błąd odczytu pliku: {str(e)}]"


async def wczytaj_kontekst_pliku(filename: str) -> str:
    """Asynchroniczne wczytanie danych z Excel — nie blokuje event loop."""
    if not filename:
        return ""

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return ""

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _wczytaj_excel_sync, file_path)


@app.post("/api/chat")
async def chat_with_ollama(
    prompt: str = Form(...),
    model: str = Form("qwen2.5:3b"),
    filename: str = Form("")
):
    """
    Asynchroniczny endpoint czatu z Ollama.
    Czyta Excel w osobnym wątku i wywołuje Ollama przez async httpx.
    """
    try:
        # Wczytaj dane z pliku asynchronicznie
        kontekst_danych = await wczytaj_kontekst_pliku(filename)

        if kontekst_danych:
            system_prompt = (
                "Jesteś asystentem analitycznym firmy Pol-Skone. "
                "Odpowiadaj wyłącznie po polsku, zwięźle i konkretnie. "
                "Analizujesz raport wad produkcyjnych. "
                "Poniżej znajdują się dane z raportu — opieraj odpowiedzi TYLKO na tych danych.\n\n"
                + kontekst_danych
            )
        else:
            system_prompt = (
                "Jesteś asystentem analitycznym firmy Pol-Skone. "
                "Odpowiadaj wyłącznie po polsku. "
                "Aktualnie żaden plik nie jest załadowany — "
                "powiedz użytkownikowi, że powinien wgrać i przetworzyć plik Excel po lewej stronie."
            )

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }

        # Asynchroniczne wywołanie Ollama — nie blokuje serwera
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()

        data = response.json()
        return {"success": True, "response": data.get("response", "Brak odpowiedzi od modelu.")}

    except httpx.ConnectError:
        return {"success": False, "error": "Nie można połączyć się z Ollama. Upewnij się, że aplikacja Ollama jest uruchomiona (http://localhost:11434)."}
    except httpx.ReadTimeout:
        return {"success": False, "error": "Ollama nie odpowiedziała w czasie 3 minut. Spróbuj zadać krótsze pytanie."}
    except Exception as e:
        return {"success": False, "error": f"Błąd podczas komunikacji z modelem: {str(e)}"}


if __name__ == "__main__":
    print("Uruchamianie serwera Pol-Skone Analiza Wad...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
