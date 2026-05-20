# Opcje wdrożenia lokalnego AI (Offline, bez zewnętrznej usługi Ollama)

Jeśli chcemy zrezygnować z wymogu instalowania i działania w tle osobnej aplikacji (jak Ollama) i chcemy "zamknąć" model AI bezpośrednio w plikach projektu (aby działał w pełni offline i był częścią aplikacji webowej), mamy do dyspozycji kilka darmowych (Open Source) ścieżek.

Zadanie, które AI ma wykonywać (odpowiadanie na pytania z potężnego arkusza kalkulacyjnego) jest trudne dla zwykłych modeli językowych, ponieważ LLM mają limity pamięci (nie wczytają tysięcy wierszy naraz). Dlatego model musi umieć "programować", by filtrować dane, zamiast je tylko czytać.

Oto najlepsze i w pełni darmowe podejście do zrealizowania tego celu.

---

## Technologia: Llama.cpp + Python (Biblioteka `llama-cpp-python`)

Zamiast osobnego serwera Ollama, możemy użyć biblioteki `llama-cpp-python`. Jest to silnik, który potrafi uruchamiać potężne modele AI bezpośrednio wewnątrz naszego obecnego serwera (pliku `app.py`).

1. **Jak to działa?**
   Pobieramy jeden plik z modelem (tzw. format `.gguf`, np. ważący około 2-4 GB) i wrzucamy go do folderu `!pliki_strony/modele`. Nasz skrypt Python ładuje ten plik do pamięci RAM komputera przy starcie aplikacji. Od tego momentu aplikacja ma "wbudowany mózg", który nie potrzebuje ani internetu, ani żadnych zewnętrznych programów.

2. **Obsługa dużego pliku Excel (Agent Pandas)**
   Ze względu na to, że `Skumulowany_Raport_Wad_PowerBI.xlsx` będzie z miesiąca na miesiąc coraz większy, sztuczna inteligencja nie może czytać go jak książki. Trzeba użyć techniki **"Text-to-Pandas"** (np. używając darmowych bibliotek *LangChain* lub *PandasAI*):
   - Użytkownik pyta: *"Który wydział miał najwięcej wad w marcu?"*
   - Nasz lokalny model AI nie próbuje "czytać" pliku – zamiast tego **pisze kod w Pythonie**, który filtruje tabelę (np. `df[df['miesiac'] == '03_2026'].groupby('Wydzial').sum()`).
   - Aplikacja wykonuje ten kod na pliku Excel, odbiera wynik (np. *"Wydział Malarni - 45 wad"*) i model AI ubiera to w ładną odpowiedź tekstową dla użytkownika.

---

## Propozycje modeli (darmowe do użytku komercyjnego i w 100% offline)

Ponieważ model ma działać na komputerze firmowym, nie może to być gigant, który "zadławi" komputer. Potrzebujemy modeli mocno "skompresowanych" (skwantyzowanych).

### 1. Qwen 2.5 (Wersja 3B lub 7B) - *Zalecany*
- **Dlaczego:** Jest fenomenalny w rozumieniu języka polskiego (znacznie lepszy niż mniejsze modele od Mety/Google'a) i wybitnie radzi sobie z pisaniem kodu (co jest kluczowe, by poprawnie wyciągał statystyki z excela poprzez PandasAI).
- **Wymagania:** Plik zajmie około 2.5 GB (dla wersji 3B) lub 4.5 GB (dla wersji 7B) miejsca na dysku.
- **Pobieranie:** Wystarczy pobrać darmowy plik z repozytorium HuggingFace (np. `qwen2.5-3b-instruct-q4_k_m.gguf`) i umieścić w folderze aplikacji.

### 2. Llama 3 (Wersja 8B)
- **Dlaczego:** Najpopularniejszy model od firmy Meta (Facebook). Bardzo inteligentny, dobrze radzi sobie z logiką, ale może czasami "gubić" język polski w bardziej złożonych zdaniach i odpowiadać po angielsku.
- **Wymagania:** Plik zajmie około 5 GB miejsca na dysku.

### 3. Mistral v0.3
- **Dlaczego:** Świetny model stworzony w Europie. Bardzo stabilny i odporny na "halucynacje" (wymyślanie danych).

---

## Jak by to wyglądało od strony instalacji?

Gdybyśmy chcieli to zrealizować, kroki wyglądałyby następująco:

1. W folderze aplikacji tworzymy folder `modele`.
2. Pobieramy plik `Qwen2.5-3B.gguf` z internetu i wrzucamy do folderu.
3. W `requirements.txt` dopisujemy `llama-cpp-python` oraz `pandasai` (lub `langchain`).
4. W pliku `app.py` zamiast wysyłać zapytania do adresu `http://localhost...` (Ollama), importujemy model bezpośrednio poleceniem `Llama(model_path="modele/Qwen2.5-3B.gguf")`.
5. Integrujemy bibliotekę `PandasAI` i wskazujemy jej, że ma rozmawiać z tym właśnie plikiem `.gguf` i pracować na pliku `Skumulowany_Raport_Wad_PowerBI.xlsx`.

## Podsumowanie zalet
- **Zero zależności:** Kopiujesz folder z programem na dowolny inny komputer w firmie (Windows), instalujesz środowisko i aplikacja po prostu działa (nie trzeba uczyć innych instalacji i włączania narzędzi deweloperskich jak Ollama).
- **Bezpieczeństwo danych:** Raporty i pytania nigdy nie opuszczają folderu aplikacji.
- **Odporność na rozmiar danych:** Dzięki metodzie "AI pisze zapytania analityczne, a komputer je wykonuje", Excel może mieć nawet 1 000 000 wierszy, a AI i tak odpowie natychmiast i bez pomyłek zliczeniowych.
