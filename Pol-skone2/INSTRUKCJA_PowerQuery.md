# Instrukcja: Automatyzacja przetwarzania danych w Power BI za pomocą Power Query

Ta metoda jest zalecana, jeśli analizą danych zajmujesz się głównie w Power BI i nie chcesz utrzymywać dodatkowych skryptów. Power Query natywnie obsługuje łączenie wielu plików o tej samej strukturze.

## Krok 1: Przygotowanie środowiska (Folder na pliki)

1. Stwórz na swoim komputerze dedykowany folder, do którego będziesz wrzucać pobrane z systemu ERP pliki. Np.:
   `C:\Users\anton\gemini_cli\Pol-skone2\Raporty_Miesieczne_Wady`
2. Gdy co miesiąc pobierasz plik `.xls` z Comarcha, przenieś go do tego folderu.
   *Dobra praktyka:* Nazywaj pliki tak, aby zawierały datę, np. `Raport_Wad_2026_03.xls`, `Raport_Wad_2026_04.xls`. Zawsze przechowuj tu **tylko** surowe raporty z ERP.

## Krok 2: Pobranie danych w Power BI

1. Otwórz swój plik raportu w Power BI Desktop.
2. Na wstążce Narzędzia główne (Home) kliknij **Pobierz dane (Get Data)** -> **Więcej (More...)**.
3. Z listy wybierz **Folder** i kliknij *Połącz (Connect)*.
4. Podaj ścieżkę do stworzonego folderu (`C:\Users\anton\gemini_cli\Pol-skone2\Raporty_Miesieczne_Wady`) i kliknij *OK*.
5. Pojawi się okno z listą plików w folderze. Na dole kliknij **Przekształć dane (Transform Data)** (lub *Połącz i Przekształć*, ale bezpieczniej jest wybrać *Przekształć dane*).

## Krok 3: Łączenie i czyszczenie w Edytorze Power Query

1. W oknie Power Query zobaczysz listę plików. W kolumnie `Content` znajdziesz ikonę z podwójną strzałką skierowaną w dół (Opcja **Połącz pliki / Combine Files**). Kliknij ją.
2. Otworzy się okno podglądu, w którym Power BI poprosi o wskazanie pliku przykładowego (zostaw "Pierwszy plik"). Wybierz główny arkusz zawierający wady i kliknij OK.
3. Power BI wygeneruje krok scalenia. Zobaczysz nową tabelę, która na początku będzie miała kolumnę `Source.Name` (nazwa oryginalnego pliku, np. `Raport_Wad_2026_03.xls`). Z tej nazwy będziesz mógł wyciągnąć informacje o dacie (np. używając "Podziel kolumnę" po znakach "_").

### Prostowanie tabeli przestrzennej z Comarch:
Z racji tego, że systemy ERP często wyrzucają dane w formie przestawnej (np. z pustymi wartościami `null` lub zagnieżdżonymi hierarchiami):
1. **Wypełnianie Wydziałów:** Zaznacz kolumnę z nazwami Wydziałów (która ma pełno wartości `null`). Kliknij na nią prawym przyciskiem myszy -> **Wypełnij (Fill)** -> **W dół (Down)**.
2. **Filtrowanie śmieci:** Otwórz filtr na kolumnie Wydziałów lub Podsumowań i odznacz wiersze, które zawierają `null` w kluczowych polach (np. Ilość) oraz odznacz z listy wiersze zawierające wyraz "Suma..." (Suma Z1WD, Suma ogólna).
3. Na koniec zmień typy danych kolumn: `Wydział` (Tekst), `Ilość` (Liczba całkowita) itp.
4. Zamknij i zastosuj zmiany (Close & Apply).

## Krok 4: Miesięczna Aktualizacja (Co miesiąc)
Od teraz Twoja praca co miesiąc wygląda tak:
1. Ściągasz plik za Kwiecień z Comarcha i wrzucasz do folderu `C:\Users\anton\gemini_cli\Pol-skone2\Raporty_Miesieczne_Wady`.
2. Otwierasz Power BI i klikasz przycisk **Odśwież (Refresh)** na stronie głównej.
3. Power BI automatycznie wczytuje kwietniowy plik, nakłada na niego wszystkie zdefiniowane reguły czyszczenia, odrzuca "sumy", wypełnia puste wiersze i dopisuje go do modelu danych. Nie musisz niczego formatować ręcznie!
