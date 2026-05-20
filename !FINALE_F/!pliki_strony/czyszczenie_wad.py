import pandas as pd
import sys
import os

def transformuj_raport(input_file, output_file=None):
    print(f"Rozpoczynam przetwarzanie pliku: {input_file} ...")
    
    try:
        # 1. Wczytanie pliku
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
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
        
        # 9. Automatyczne generowanie nazwy pliku wyjściowego, jeśli nie podano własnej
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_forPowerFI.xlsx"
            
        # 10. Zapis do Excela
        df_long.to_excel(output_file, index=False)
        print(f"Sukces! Wyczyszczone dane zapisano w: {output_file}")
        
        # Dodajemy zwracanie metadanych do wykorzystania przez interfejs webowy
        return {
            "success": True,
            "output_path": output_file,
            "records_count": len(df_long)
        }
        
    except FileNotFoundError:
        return {"success": False, "error": f"BŁĄD: Nie znaleziono pliku '{input_file}'. Upewnij się, że nazwa jest poprawna."}
    except Exception as e:
        return {"success": False, "error": f"Wystąpił nieoczekiwany błąd: {e}"}

# ---------------------------------------------------------
# Sekcja uruchamiania z terminala (wiersza poleceń)
# ---------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        plik_wejsciowy = sys.argv[1]
        transformuj_raport(plik_wejsciowy)
    else:
        print("Użycie narzędzia:")
        print('python czyszczenie_wad.py "nazwa_twojego_pliku.xlsx"')
