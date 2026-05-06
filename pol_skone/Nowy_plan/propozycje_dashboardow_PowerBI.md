# Koncepcja Systemu Raportowania Jakości (Power BI)

Jako ekspert w dziedzinie analityki biznesowej i wizualizacji danych, przeanalizowałem dostarczone struktury danych z plików:
- `raport wad marzec 2026 - katalog.xlsx` (dane surowe, zagnieżdżone)
- `raport wad marzec 2026 - katalog_PowerBI.xlsx` (dane ustrukturyzowane)

**Wniosek z analizy wejścia:**
*   Plik surowy jest tzw. plikiem "pivotowanym" (układ tabeli przestawnej dla człowieka), zawierającym puste komórki i scalaną strukturę – to anty-wzorzec dla Power BI, bardzo trudny do modelowania.
*   Plik z dopiskiem `_PowerBI` został prawidłowo "odpivortowany" (tzw. struktura płaska / unpivot). Składa się on z kolumn: `Wydział`, `Kierunek`, `Grupa ogólna`, `Wada`, `Ilość`. Ta struktura to idealna podstawa jako **Tabela Faktów (Fact Table)** dla Power BI.

Poniżej przedstawiam docelowy projekt rozwiązań analitycznych zgodnie z Twoimi wymaganiami.

---

## 1. Identyfikacja kluczowych wskaźników (KPI) i Grup Docelowych

### Grupa docelowa A: Zarząd (Board of Directors)
*   **Perspektywa:** Strategiczna, finansowa, całościowy ogląd (helicopter view).
*   **Zdefiniowane potrzeby:** Informacja, czy jakość na rynkach eksportowych i krajowych spełnia standardy oraz gdzie organizacja ponosi straty.
*   **Kluczowe KPI:** 
    *   Całkowita ilość wad (*Total Defects*) - z dostarczonych danych.
    *   Koszt złej jakości (*Cost of Poor Quality - COPQ*) - **BRAK DANYCH**.
    *   Wskaźnik wadliwości względem całkowitej produkcji (np. *PPM - Parts Per Million*) - **BRAK DANYCH**.

### Grupa docelowa B: Kierownik Produkcji (Production Manager)
*   **Perspektywa:** Operacyjna, procesowa, poszukiwanie wąskich gardeł (bottlenecks).
*   **Zdefiniowane potrzeby:** Szybka diagnoza – który dział ma problemy, przy jakim produkcie i jaki konkretnie jest to błąd, aby natychmiast korygować ustawienia maszyn czy szkolić brygady.
*   **Kluczowe KPI:**
    *   Liczba wad w ujęciu per Wydział i Grupa Ogólna - z dostarczonych danych.
    *   Top 5 najczęstszych przyczyn wad (*Defect Pareto*) - z dostarczonych danych.
    *   Trend pojawiania się wad (dni tygodnia/tygodnie) - **BRAK DANYCH** (dane są tylko zagregowane dla "marca").

---

## 2. Propozycje 3 dedykowanych Dashboardów

Wszystkie dashboardy powinny posiadać globalne filtry (Slicers) umieszczone na górze lub po lewej stronie ekranu: `Wydział`, `Kierunek`, `Grupa ogólna`. Gwarantuje to oczekiwaną interaktywność i drążenie danych.

### Dashboard 1: Executive Quality Overview (Dla Zarządu)
**Cel:** Błyskawiczna informacja o całkowitej skali problemów jakościowych z podziałem na kluczowe rynki zbytu.

*   **Wizualizacja 1 (Karty KPI / KPI Cards):** Główny kafel z liczbą: `Łączna liczba wad` (suma kolumny Ilość). 
    *   *Brak Danych:* Obok powinna znaleźć się karta `Szacowana Strata Finansowa`. Aby to dodać, potrzebujemy stworzyć słownik ze średnimi kosztami błędu.
*   **Wizualizacja 2 (Wykres Pierścieniowy / Donut Chart):** Udział wad ze względu na `Kierunek` (PL vs EX). Pełni też funkcję filtru interaktywnego - kliknięcie w wycinek "EX" filtruje cały raport pokazując strukturę wad tylko dla eksportu.
*   **Wizualizacja 3 (Wykres Kolumnowy Skumulowany / Stacked Column):** Oś X: `Wydział`. Oś Y: `Ilość`. Legenda (kolory): `Grupa ogólna`. Pozwala szybko wzrokowo ocenić, który z wydziałów generuje najwięcej braków w jakich asortymentach (Futryny, Drzwi).
*   **Wizualizacja 4 (Wykres Liniowy Trendu):** **BRAK DANYCH.** Zazwyczaj to serce raportu zarządu. Brakuje nam osi czasu (daty wystąpienia wady). Zamiast tego proponuję alternatywę: **Wykres Drzewa (Treemap)** pokazujący ogólny udział poszczególnych rodzajów wad w pigułce.

### Dashboard 2: Production Quality Control (Dla Kierownika Produkcji)
**Cel:** Narzędzie do pracy na codziennych spotkaniach statusowych i wyszukiwania przyczyn źródłowych (Root Cause Analysis).

*   **Wizualizacja 1 (Wykres Pareto / Line and Clustered Column):** Zastosowanie zasady 80/20. Oś X: `Wada` (np. "błąd frezowania"). Oś Y słupki: `Ilość` malejąco. Linia: Skumulowany %. Wykres od razu mówi Kierownikowi: *"Skup się dzisiaj na poprawie ustawień frezarki na Z1WD, to rozwiąże 40% naszych dzisiejszych wad"*.
*   **Wizualizacja 2 (Macierz / Matrix):** Tabela do analizy przekrojowej. Wiersze z możliwością rozwijania (Drill-down): `Wydział` -> klikamy plus (+) -> rozwija się do `Grupa ogólna` -> `Wada`. Opcja *Formatowanie Warunkowe* nakłada kolory (Heatmapa) na najwyższe wartości kolumny `Ilość`.
*   **Wizualizacja 3 (Drzewo Dekompozycji / Decomposition Tree):** Rozwiązanie AI w Power BI. Rozpoczynamy od "Całkowitej Ilości Wad" i pozwalamy programowi samodzielnie zidentyfikować gałęzie odchyleń w dół aż do konkretnego powodu wady.

### Dashboard 3: Cross-Analysis: Market vs. Defect (Analityczny / Dla Jakości)
**Cel:** Głęboka diagnoza różnic pomiędzy rynkami. Ustalenie czy wysyłki eksportowe mają inną charakterystykę problemów niż krajowe.

*   **Wizualizacja 1 (Skonfrontowany Wykres Barowy / Tornado Chart):** Pionowa lista `Wada` na środku. Lewa strona to słupki dla Polski (PL), prawa dla Eksportu (EX). Błyskawicznie kontrastuje profil wad obu kierunków.
*   **Wizualizacja 2 (Kluczowe Czynniki Wpływające / Key Influencers):** Wizualizacja AI odpowiadająca na pytanie: "Co wpływa na to, że wada występuje?". Power BI sam znajduje korelacje, np.: *"Prawdopodobieństwo wystąpienia błędu malowania wzrasta 3x, gdy Kierunek to EX a Wydział to Z2WF"*.
*   **Wizualizacja 3 (Tabela Szczegółowa do eksportu):** 
    *   *Brak Danych:* Do pełnego obrazu operacyjnego brakuje nam numerów poszczególnych partii (Batch ID/Nr Zlecenia), dzięki którym inżynier jakości mógłby zejść z poziomu Power BI na halę produkcyjną i sprawdzić konkretny produkt.

---

## 3. Luki w Danych (Data Gaps) - Rekomendacje dla IT/ERP

Model `katalog_PowerBI.xlsx` pozwala na świetną, lecz "statyczną" analizę. Aby przejść od prostego raportowania do prawdziwego *Business Intelligence*, należy pozyskać następujące dane z systemu ERP:

1.  **Data i Czas (Time Intelligence):** Bez kolumny `Data Zgłoszenia` lub `Data Wykrycia`, niemożliwe jest badanie trendów (czy wadliwość w drugim tygodniu marca spadła po szkoleniu pracowników?), analizowanie dni tygodnia (czy w piątki jest więcej braków?) ani porównywanie *Rok do Roku / Miesiąc do Miesiąca*.
2.  **Wolumen (Mianownik do ułamka):** Posiadamy tylko liczniki (ile było wad). Nie wiemy, czy 10 zepsutych drzwi na wydziale Z2WF to ułamek promila dla 10 000 wyprodukowanych (bardzo dobrze), czy aż 10% ze 100 wyprodukowanych sztuk (bardzo źle). Potrzebne są dane o wolumenie produkcji.
3.  **Koszty (Finanse):** Różne wady niosą różny koszt. Rysa to koszt zaprawki, a pęknięcie to konieczność wyprodukowania futryny od nowa. Potrzebny jest estymowany koszt dla poszczególnych grup/typów.
4.  **Granulacja Operacyjna (Kontekst):** Kolumny takie jak `Zmiana (1,2,3)`, `Maszyna`, `Osoba kontrolująca`. To one sprawiają, że raport staje się narzędziem Action-Oriented i pozwala podejmować konkretne kroki naprawcze.

## 4. Wdrażanie w Power BI (Best Practices)
*   **Model Danych:** Zbuduj strukturę zwaną *Modelem Gwiazdy (Star Schema)*. "Odcięcie" powtarzających się nazw wydziałów i kierunków do małych tabel słownikowych drastycznie poprawi wydajność i filtrowanie.
*   **Język DAX:** Nie ufaj domyślnym podsumowaniom PBI. Napisz tzw. *Explicit Measures* (Miary Skuteczne), np.: `Ilosc Wad = SUM('Tabela_Faktow'[Ilość])`.
*   **Złota zasada kolorów:** Dashboardy nie powinny przypominać tęczy. Używaj spójnych, stonowanych odcieni szarości lub kolorów firmowych. Użyj silnych barw (np. **czerwonego**) tylko i wyłącznie jako *Call to Action* – do podświetlenia miejsc, gdzie przekroczono dopuszczalny próg błędu (np. za pomocą formatowania warunkowego w Macierzy).
