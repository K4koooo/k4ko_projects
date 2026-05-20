import pandas as pd
import os
import glob
import shutil
import re

def parse_month_year(filename):
    filename_lower = filename.lower()
    miesiace = {
        'styczen': '01', 'styczeń': '01',
        'luty': '02',
        'marzec': '03',
        'kwiecien': '04', 'kwiecień': '04',
        'maj': '05',
        'czerwiec': '06',
        'lipiec': '07',
        'sierpien': '08', 'sierpień': '08',
        'wrzesien': '09', 'wrzesień': '09',
        'pazdziernik': '10', 'październik': '10',
        'listopad': '11',
        'grudzien': '12', 'grudzień': '12'
    }
    
    rok_match = re.search(r'\d{4}', filename_lower)
    rok = rok_match.group(0) if rok_match else '0000'
    
    miesiac = '00'
    for nazwa, numer in miesiace.items():
        if nazwa in filename_lower:
            miesiac = numer
            break
            
    if miesiac == '00':
        mm_match = re.search(r'_(\d{2})[_\.]', filename_lower)
        if mm_match:
            miesiac = mm_match.group(1)
            
    return f"{miesiac}_{rok}"

# --- TU MIEJSCE NA TWOJE IMPORTY / ZMIENNE ---


# ---------------------------------------------

# 1. Konfiguracja ścieżek
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'Nowe_Raporty_ERP')
OUTPUT_FILE = os.path.join(BASE_DIR, 'Skumulowany_Raport_Wad_PowerBI.xlsx')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'Archiwum_Raportow')

# Upewniamy się, że foldery istnieją
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def process_single_file(filepath):
    """
    Funkcja czyszcząca pojedynczy raport surowy wg logiki.
    Należy ją dostosować do dokładnego zagnieżdżenia ERP Comarch.
    """
    # 1. Wczytanie pliku
    df = pd.read_excel(filepath, sheet_name=0, header=None)
    
    # 2. Wyciągnięcie nagłówków wad z 6. wiersza (indeks 5)
    wady_kolumny = df.iloc[5, 13:-1].values
    
    # 3. Ograniczenie tabeli do wierszy z danymi
    df_data = df.iloc[7:].copy()
    
    # 4. Przypisywanie i wypełnianie wymiarów
    df_data['Wydział'] = df_data[0].ffill()
    df_data['Kierunek'] = df_data[8].ffill()
    df_data['Grupa ogólna'] = df_data[11].ffill()
    
    # 5. Wyodrębnienie części z ilością wad
    df_wady = df_data.iloc[:, 13:13+len(wady_kolumny)].copy()
    df_wady.columns = wady_kolumny
    
    # 6. Złączenie w jedną tabelę i transformacja 'melt' (szeroka -> długa)
    df_cleaned = pd.concat([df_data[['Wydział', 'Kierunek', 'Grupa ogólna']], df_wady], axis=1)
    df_long = pd.melt(
        df_cleaned, 
        id_vars=['Wydział', 'Kierunek', 'Grupa ogólna'],
        var_name='Wada',
        value_name='Ilość'
    )
    
    # 7. Czyszczenie: usuwanie pustych zgłoszeń
    df_long = df_long.dropna(subset=['Ilość'])
    df_long = df_long[df_long['Ilość'] > 0]
    df_long['Ilość'] = df_long['Ilość'].astype(int)
    
    # 8. NOWOŚĆ: Usuwanie "Sum" podsumowujących z tabeli przestawnej
    df_long = df_long[~df_long['Wydział'].astype(str).str.contains('(?i)suma')]
    df_long = df_long[~df_long['Kierunek'].astype(str).str.contains('(?i)suma')]
    
    # Resetowanie indeksu
    df_long = df_long.reset_index(drop=True)
    
    # Jako znacznik dodajemy wyciągnięty miesiąc i rok (MM_YYYY)
    filename = os.path.basename(filepath)
    df_long['Zrodlo_Miesiac'] = parse_month_year(filename)
    
    return df_long

def main():
    # Pobierz listę wszystkich nowych plików .xls / .xlsx
    new_files = glob.glob(os.path.join(INPUT_DIR, '*.xls*'))
    
    if not new_files:
        print(f"Brak nowych plików do przetworzenia w folderze {INPUT_DIR}.")
        return
        
    all_new_data = []
    
    for file in new_files:
        print(f"Przetwarzam: {file}")
        cleaned_df = process_single_file(file)
        all_new_data.append(cleaned_df)
        
        # Przeniesienie do archiwum po poprawnym dodaniu do listy
        filename = os.path.basename(file)
        archive_path = os.path.join(ARCHIVE_DIR, filename)
        shutil.move(file, archive_path)
        print(f"Zarchiwizowano plik: {filename}")
        
    # Sklejenie wszystkich nowych miesięcy
    df_new = pd.concat(all_new_data, ignore_index=True)
    
    # Zapisanie/dopisanie do pliku głównego (append)
    if os.path.exists(OUTPUT_FILE):
        df_master = pd.read_excel(OUTPUT_FILE)
        df_master = pd.concat([df_master, df_new], ignore_index=True)
    else:
        df_master = df_new
        
    df_master.to_excel(OUTPUT_FILE, index=False)
    print(f"Dodano i zapisano nowe dane w: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
