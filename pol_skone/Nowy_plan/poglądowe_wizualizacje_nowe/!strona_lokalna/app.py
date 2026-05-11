from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import shutil
import os
from czyszczenie_wad import transformuj_raport
import requests

app = FastAPI(title="Pol-Skone Analiza Wad")

# Utworzenie folderu na tymczasowe pliki jeśli nie istnieje
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Konfiguracja plików statycznych i szablonów
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Domyślny URL dla lokalnej instancji Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.post("/api/process-file")
async def process_file(file: UploadFile = File(...)):
    try:
        # Zapisz plik lokalnie
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Wywołaj skrypt czyszczący
        # Plik wynikowy zostanie zapisany w folderze uploads z odpowiednią nazwą
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}_forPowerFI.xlsx"
        output_path = os.path.join(UPLOAD_DIR, output_filename)
        
        result = transformuj_raport(file_location, output_path)
        
        if result.get("success"):
            return {
                "success": True, 
                "message": f"Znaleziono {result['records_count']} unikalnych zgłoszeń. Plik gotowy do pobrania.",
                "download_url": f"/api/download/{output_filename}"
            }
        else:
            return {"success": False, "error": result.get("error", "Nieznany błąd podczas przetwarzania.")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return {"error": "Plik nie istnieje."}

@app.post("/api/chat")
async def chat_with_ollama(prompt: str = Form(...), model: str = Form("qwen3.6")):
    """
    Prosty endpoint przekazujący zapytanie do lokalnej instancji Ollama.
    Na tym etapie działa jako przelotka (proxy) do lokalnego modelu.
    """
    try:
        # Przykładowy system prompt ustawiający kontekst dla modelu
        system_prompt = "Jesteś asystentem analitycznym firmy Pol-Skone. Twoim zadaniem jest pomoc w analizie danych z raportów wad produkcyjnych."
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        # Wywołanie lokalnego API Ollamy
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return {"success": True, "response": data.get("response", "Brak odpowiedzi od modelu.")}
        
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Nie można połączyć się z serwerem Ollama. Upewnij się, że aplikacja Ollama jest uruchomiona (http://localhost:11434)."}
    except Exception as e:
        return {"success": False, "error": f"Wystąpił błąd podczas komunikacji z modelem: {str(e)}"}

if __name__ == "__main__":
    print("Uruchamianie serwera Pol-Skone Analiza Wad...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
