#!/bin/bash
set -e

echo "=== Door Defects Chatbot Backend ==="
echo "Ollama (host): ${OLLAMA_BASE_URL}"
echo "LLM model:     ${LLM_MODEL}"
echo "Embed model:   ${EMBED_MODEL}"

# Nieblokujące sprawdzenie Ollama — backend startuje niezależnie od jej dostępności
if curl -sf --max-time 3 "${OLLAMA_BASE_URL}/api/tags" > /dev/null 2>&1; then
    echo "Ollama dostępna. Sprawdzanie modeli..."
    TAGS=$(curl -sf "${OLLAMA_BASE_URL}/api/tags" 2>/dev/null || echo "{}")
    for MODEL in "${LLM_MODEL}" "${EMBED_MODEL}"; do
        if echo "${TAGS}" | grep -qi "${MODEL}"; then
            echo "Model ${MODEL}: dostepny."
        else
            echo "Pobieranie modelu: ${MODEL} (to moze potrwac kilka minut)..."
            curl -sS -X POST "${OLLAMA_BASE_URL}/api/pull" \
                -H "Content-Type: application/json" \
                -d "{\"name\": \"${MODEL}\"}" | tail -1
            echo "Model ${MODEL} gotowy."
        fi
    done
else
    echo ""
    echo "  UWAGA: Ollama niedostepna pod ${OLLAMA_BASE_URL}"
    echo "  Uruchom Ollama na hoscie: ollama serve"
    echo "  Backend startuje — polacy sie z Ollama gdy bedzie dostepna."
    echo ""
fi

echo "Uruchamianie serwera FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info
