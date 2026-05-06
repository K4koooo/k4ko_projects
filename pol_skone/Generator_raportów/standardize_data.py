import pandas as pd
import os
import glob
import sys

def find_latest_report(input_dir):
    files = glob.glob(os.path.join(input_dir, "*.xls*"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def standardize():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'Pliki_do_analizy')
    
    # Wybór folderu zapisu
    output_dir = sys.argv[1] if len(sys.argv) > 1 else base_dir
    output_csv = os.path.join(output_dir, 'raport_clean.csv')

    file_path = find_latest_report(input_dir)
    if not file_path:
        print(f"BŁĄD: Nie znaleziono pliku w {input_dir}")
        return False
    
    print(f"Przetwarzam plik: {os.path.basename(file_path)}")

    category_map = {
        'PRODUKCJA': ['Błąd produkcji', 'Niezgodność z zamówieniem', 'Brak w dostawie', 'Błąd frezowania', 'wymiary', 'konfiguracja'],
        'KONSTRUKCJA': ['Wada konstrukcji', 'Pęknięcie', 'Wypaczenie', 'rozklejanie', 'ramiaka', 'skrzydła'],
        'POWIERZCHNIA': ['Wada powierzchni', 'foli', 'farby', 'obrzeża', 'ecotop', 'laminat', 'okleinowana', 'malowana', 'łuszczenie'],
        'OKUCIA': ['Wada okuć', 'zamek', 'zamka', 'zawiasów', 'zawiasy', 'Hobes', 'LOB', 'Hafele'],
        'LOGISTYKA': ['Brak w dostawie', 'wydania z magazynu', 'Uszkodzenia mechaniczne', 'Uszkodzenia mechanczne', 'szyby', 'rysy', 'obicia']
    }

    def map_to_category(name):
        name_lower = str(name).lower()
        for cat, keywords in category_map.items():
            if any(kw.lower() in name_lower for kw in keywords):
                return cat
        return 'INNE'

    try:
        df_raw = pd.read_excel(file_path, header=None)
        headers = df_raw.iloc[5].tolist()
        wydzialy = df_raw.iloc[7:, 0].ffill()
        mask = ~wydzialy.str.contains('Suma|ogólna', case=False, na=False)
        data_indices = wydzialy[mask].index
        final_rows = []
        for i in range(11, df_raw.shape[1] - 1):
            v_name = str(headers[i])
            v_cat = map_to_category(v_name)
            v_values = pd.to_numeric(df_raw.iloc[data_indices, i], errors='coerce').fillna(0)
            for idx, val in zip(data_indices, v_values):
                if val > 0:
                    final_rows.append({'Wydzial': wydzialy.loc[idx], 'Oryginalna_Wada': v_name, 'Kategoria': v_cat, 'Ilosc': val})
        df_clean = pd.DataFrame(final_rows)
        df_clean.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"SUKCES: Dane ustandaryzowane w {output_csv}")
        return True
    except Exception as e:
        print(f"BŁĄD: {e}")
        return False

if __name__ == "__main__":
    standardize()
