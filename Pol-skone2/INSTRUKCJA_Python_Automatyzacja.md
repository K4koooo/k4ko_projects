# Instrukcja: Automatyzacja przy pomocy skryptu Python

To rozwiązanie jest idealne, jeśli chcesz zbudować bazę wad i używać jej również poza Power BI (np. na potrzeby sztucznej inteligencji, raportów mailowych lub integracji z innymi systemami jak baza wektorowa dla czatbota LLM). 

Python sprawdzi wszystkie nowe pliki ze zrzutu z ERP i połączy je ze starymi w jeden czysty, "płaski" zbiór `.xlsx` z którym potem w łatwy sposób pracuje PowerBI i AI.

## Krok 1: Organizacja plików

1. Utwórz w głównym katalogu (lub w `Pol-skone2`) folder, w którym będziesz umieszczał pobrane pliki wejściowe, np. folder o nazwie `Nowe_Raporty_ERP`.
2. Główne dane czyste będą przechowywane w pliku zbiorczym, np. `Wszystkie_Wady_PowerBI.xlsx`.

## Krok 2: Skrypt Python

Stwórz w folderze `Pol-skone2` plik o nazwie `append_reports.py` (lub dodaj ten kod jako nowy moduł w ramach swojego systemu czatbota/aplikacji internetowej). Poniżej znajduje się przykładowa logika (będzie wymagać dostosowania pod dokładny format pliku Comarch w pandas, ale ogólny schemat to tzw. "bulk processing").

```python
import pandas as pd
import os
import glob

# 1. Konfiguracja ścieżek
INPUT_DIR = 'Nowe_Raporty_ERP'
OUTPUT_FILE = 'Wszystkie_Wady_PowerBI.xlsx'
ARCHIVE_DIR = 'Archiwum_Raportow' # Gdzie przenieść pliki po przetworzeniu (aby ich 2x nie czytać)

def process_single_file(filepath):
    """
    Funkcja czyszcząca pojedynczy raport surowy wg logiki.
    Należy ją dostosować do dokładnego zagnieżdżenia ERP Comarch.
    """
    # Wczytanie pliku
    df = pd.read_excel(filepath)
    
    # Przykładowa logika czyszczenia struktury Comarch z pliku XLS:
    # a) Odrzucenie 4 pierwszych nagłówków
    # df = df.iloc[4:].reset_index(drop=True)
    
    # b) "Wypełnij w dół" dla wydziałów z uwagi na tabele przestawną
    # df['Wydzial'] = df['Wydzial'].ffill()
    
    # c) Odrzucenie podsumowań (np. Suma Z1WD)
    # df = df[~df['Wydzial'].astype(str).str.contains('Suma')]
    
    # Zwracamy wyczyszczoną "płaską" ramkę danych np:
    # Wydział | Kierunek | Grupa ogólna | Wada | Ilość | Plik_Zrodlowy
    
    # Jako znacznik dodajemy nazwę pliku lub datę
    df['Zrodlo_Miesiac'] = os.path.basename(filepath)
    
    return df

def main():
    # Pobierz listę wszystkich nowych plików .xls / .xlsx
    new_files = glob.glob(os.path.join(INPUT_DIR, '*.xls*'))
    
    if not new_files:
        print("Brak nowych plików do przetworzenia.")
        return
        
    all_new_data = []
    
    for file in new_files:
        print(f"Przetwarzam: {file}")
        cleaned_df = process_single_file(file)
        all_new_data.append(cleaned_df)
        
    # Sklejenie wszystkich nowych miesięcy
    df_new = pd.concat(all_new_data, ignore_index=True)
    
    # Zapisanie/dopisanie do pliku głównego (append)
    if os.path.exists(OUTPUT_FILE):
        df_master = pd.read_excel(OUTPUT_FILE)
        df_master = pd.concat([df_master, df_new], ignore_index=True)
    else:
        df_master = df_new
        
    df_master.to_excel(OUTPUT_FILE, index=False)
    print(f"Dodano i zapisano dane w: {OUTPUT_FILE}")
    
    # Opcjonalnie: przenieś pliki z INPUT_DIR do ARCHIVE_DIR (wymaga biblioteki shutil)

if __name__ == '__main__':
    main()
```

## Krok 3: Automatyzacja 

Gdy skrypt jest napisany, wszystko czego potrzebujesz to uruchomić raz w miesiącu po wyciągnięciu pliku z ERP:
1. Zapisz `.xls` z Comarcha w `Nowe_Raporty_ERP`.
2. Uruchom skrypt (np. podpinając to pod przycisk w Twoim nowym interfejsie webowym). Skrypt wyczyści plik, doklei go do `Wszystkie_Wady_PowerBI.xlsx` i zarchiwizuje oryginał.
3. Power BI podpięty pod `Wszystkie_Wady_PowerBI.xlsx` załaduje od razu nowe, połączone dane z całego roku po wciśnięciu *Odśwież*.
