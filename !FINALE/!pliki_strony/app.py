from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import shutil
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import sys

# Dodajemy !FINALE do ścieżki
FINALE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FINALE_DIR not in sys.path:
    sys.path.append(FINALE_DIR)

from append_reports import process_single_file, OUTPUT_FILE, ARCHIVE_DIR
app = FastAPI(title="Pol-Skone Analiza Wad")

# Pula wątków do operacji blokujących (I/O plik, pandas)
executor = ThreadPoolExecutor(max_workers=4)

# Utworzenie folderu na tymczasowe pliki jeśli nie istnieje
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Konfiguracja plików statycznych i szablonów
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# URL Ollamy (startuje automatycznie z Windowsem)
OLLAMA_BASE_URL = "http://localhost:11434"

# Aktywny plik kontekstu (aktualizowany po każdym przetworzeniu)
active_processed_file: str = ""


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


def process_and_append(file_location):
    try:
        # 1. Przetworzenie pliku
        df_new = process_single_file(file_location)
        
        # 2. Dodanie do pliku głównego
        if os.path.exists(OUTPUT_FILE):
            df_master = pd.read_excel(OUTPUT_FILE)
            df_master = pd.concat([df_master, df_new], ignore_index=True)
        else:
            df_master = df_new
            
        df_master.to_excel(OUTPUT_FILE, index=False)
        
        # 3. Przeniesienie do archiwum
        filename = os.path.basename(file_location)
        archive_path = os.path.join(ARCHIVE_DIR, filename)
        shutil.move(file_location, archive_path)
        
        return {"success": True, "records_count": len(df_new)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/process-file")
async def process_file(file: UploadFile = File(...)):
    global active_processed_file
    try:
        # Zapisz plik lokalnie
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Wywołaj skrypt czyszczący i dołączający
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, process_and_append, file_location
        )

        if result.get("success"):
            active_processed_file = os.path.basename(OUTPUT_FILE)
            return {
                "success": True,
                "message": f"Dodano do bazy pomyślnie. Nowe wiersze: {result['records_count']}.",
                "processed_filename": active_processed_file
            }
        else:
            return {"success": False, "error": result.get("error", "Nieznany błąd.")}

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/current-file")
async def get_current_file():
    """
    Zwraca nazwę ostatnio przetworzonego pliku.
    """
    if active_processed_file:
        path = os.path.join(UPLOAD_DIR, active_processed_file)
        if os.path.exists(path):
            return {"filename": active_processed_file}

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


@app.get("/api/download/master")
async def download_master():
    if os.path.exists(OUTPUT_FILE):
        return FileResponse(
            path=OUTPUT_FILE,
            filename=os.path.basename(OUTPUT_FILE),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    return {"error": "Plik główny nie istnieje."}

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


def _run_pandas_agent_sync(file_path: str, prompt: str, model: str) -> str:
    """
    Uruchamia LangChain Pandas Agent z Ollama jako LLM.
    Wykonywane w osobnym wątku (nie blokuje event loop).
    """
    try:
        from langchain_community.llms import Ollama
        from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

        df = pd.read_excel(file_path)

        llm = Ollama(
            base_url=OLLAMA_BASE_URL,
            model=model,
            temperature=0.0,
            timeout=180,
        )

        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
        )

        odpowiedz = agent.run(
            f"Odpowiedz po polsku, zwięźle i konkretnie. Pytanie: {prompt}"
        )
        return str(odpowiedz)

    except Exception as e:
        raise RuntimeError(str(e))


@app.post("/api/chat")
async def chat(
    prompt: str = Form(...),
    model: str = Form("qwen2.5:3b"),
    filename: str = Form("")
):
    """
    Endpoint czatu — używa LangChain Pandas Agent z Ollama.
    Agent nie czyta surowego tekstu pliku, lecz pisze kod Python
    analizujący pełny DataFrame — dokładny dla dowolnej liczby wierszy.
    """
    # Ustal ścieżkę do pliku danych
    if not filename:
        return {"success": False, "error": "Brak wybranego pliku. Przetwórz plik Excel przed zadaniem pytania."}

    if filename == os.path.basename(OUTPUT_FILE):
        file_path = OUTPUT_FILE
    else:
        file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        return {"success": False, "error": f"Nie znaleziono pliku: {filename}"}

    try:
        loop = asyncio.get_event_loop()
        odpowiedz = await loop.run_in_executor(
            executor,
            _run_pandas_agent_sync,
            file_path,
            prompt,
            model
        )
        return {"success": True, "response": odpowiedz}

    except RuntimeError as e:
        err = str(e)
        if "ConnectError" in err or "Connection refused" in err or "connect" in err.lower():
            return {
                "success": False,
                "error": "Nie można połączyć się z Ollama. Upewnij się, że aplikacja Ollama jest uruchomiona (http://localhost:11434)."
            }
        return {"success": False, "error": f"Błąd podczas analizy danych: {err}"}
    except Exception as e:
        return {"success": False, "error": f"Nieoczekiwany błąd: {str(e)}"}


if __name__ == "__main__":
    print("Uruchamianie serwera Pol-Skone Analiza Wad...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
