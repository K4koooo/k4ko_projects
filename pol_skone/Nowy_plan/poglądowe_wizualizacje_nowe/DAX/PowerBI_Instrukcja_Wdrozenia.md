# Instrukcja Wdrożenia Dashboardów w Power BI

W tym przewodniku znajdziesz kroki niezbędne do samodzielnego "wyklikania" 3 interaktywnych dashboardów w aplikacji Power BI Desktop. Wykorzystamy do tego gotowy plik z Twoimi danymi.

## 1. Import i Przygotowanie Danych
1. Otwórz program **Power BI Desktop**.
2. Kliknij **Pobierz dane (Get Data)** z głównej wstążki i wybierz **Skoroszyt programu Excel (Excel workbook)**.
3. Wskaż plik `raport wad marzec 2026 - katalog_PowerBI.xlsx`.
4. W oknie Nawigatora zaznacz arkusz z danymi (prawdopodobnie "Arkusz1") i kliknij **Załaduj (Load)**.
5. Po prawej stronie w panelu **Dane (Data)** pojawi się Twoja tabela. Dla wygody kliknij na nią prawym przyciskiem myszy i zmień jej nazwę na `Tabela_Wad`.

## 2. Tworzenie profesjonalnych miar (DAX)
W profesjonalnych raportach unikamy przeciągania surowych kolumn do wykresów. Zamiast tego stosuje się miary.
1. Kliknij prawym przyciskiem myszy na załadowaną `Tabela_Wad` i wybierz **Nowa miara (New measure)**.
2. Otwórz dołączony plik `DAX_miary.txt`. Skopiuj pierwszą formułę, np. `Suma Wad = SUM('Tabela_Wad'[Ilość])`.
3. Wklej ją w pasku formuły u góry ekranu i zatwierdź (Enter).
4. Powtórz te kroki dla wszystkich przygotowanych miar.

## 3. Budowa Dashboardu 1: Executive Quality Overview (Zarząd)
Dodaj nową stronę na dole ekranu i nazwij ją "Executive". Z panelu wizualizacji wybierz poszczególne wykresy i przypisz do nich dane w następujący sposób:

*   **Karty KPI:**
    *   Wybierz wizualizację **Karta (Card)** (ikona z numerem 123). W pole *Pola (Fields)* przeciągnij miarę `Suma Wad`.
    *   Utwórz drugą kartę i przeciągnij do niej miarę `Szacowana Strata Finansowa`.
*   **Wykres Pierścieniowy (Donut Chart):**
    *   Wybierz **Wykres pierścieniowy**.
    *   *Legenda:* pole `Kierunek` z tabeli.
    *   *Wartości:* miara `Suma Wad`.
*   **Wykres Kolumnowy Skumulowany:**
    *   Wybierz **Skumulowany wykres kolumnowy**.
    *   *Oś X:* `Wydział`.
    *   *Oś Y:* `Suma Wad`.
    *   *Legenda:* `Grupa ogólna`.
*   **Wykres Drzewa (Treemap):**
    *   Wybierz **Mapa drzewa** (ikona złożona z prostokątów).
    *   *Kategoria:* `Wada`.
    *   *Wartości:* `Suma Wad`.

## 4. Budowa Dashboardu 2: Production Quality Control (Kierownik)
Dodaj drugą stronę "Production".

*   **Wykres Pareto:**
    *   Wybierz **Wykres kolumnowy i liniowy (Line and clustered column chart)**.
    *   *Oś X:* `Wada`.
    *   *Oś Y dla kolumn:* miara `Suma Wad`.
    *   *Oś Y dla linii:* opcjonalnie `Suma Wad` z włączoną szybką analizą "Procent sumy końcowej" lub nasza miara `% Wad`.
    *   Upewnij się, że posortowałeś wykres malejąco (ikona 3 kropek nad wykresem -> Sortuj oś).
*   **Macierz (Matrix) - Heatmapa:**
    *   Wybierz **Macierz**.
    *   *Wiersze:* Przeciągnij `Wydział`, poniżej `Grupa ogólna`, a poniżej `Wada` (stworzy to hierarchię rozwijaną plusem `+`).
    *   *Wartości:* miara `Suma Wad`.
    *   *Formatowanie Warunkowe:* Kliknij na pędzelek (Formatuj wizualizację) -> *Elementy komórki* -> włącz suwak *Kolor Tła* dla Sumy Wad.

## 5. Budowa Dashboardu 3: Cross-Analysis (Analityczny)
Dodaj trzecią stronę "Cross-Analysis".

*   **Kluczowe Czynniki Wpływające (Key Influencers):**
    *   Z panelu wizualizacji wybierz **Kluczowe czynniki wpływające** (ikona z lupką lub sztuczną inteligencją).
    *   *Analizuj:* miara `Suma Wad`.
    *   *Wyjaśnij wg:* przeciągnij wszystkie wymiary analityczne: `Wydział`, `Kierunek`, `Grupa ogólna`.
    *   Power BI sam obliczy zależności i wygeneruje tekstowe podsumowania wraz z małymi wykresami!
*   **Skonfrontowany Wykres Barowy:**
    *   Standardowo możesz zestawić obok siebie dwa skumulowane wykresy paskowe.
    *   Alternatywnie, wejdź w trzy kropki w panelu wizualizacji `...` -> **Pobierz więcej wizualizacji (Get more visuals)** i wyszukaj darmowy dodatek "Tornado Chart" (od Microsoft), by uzyskać piękny wykres w stylu lustrzanego odbicia dla Polski vs Eksport.
