import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'
output_dir = r'C:\Users\anton\gemini_cli\pol_skone'

try:
    # 1. Odczyt danych
    df_raw = pd.read_excel(file_path, header=None)
    headers_raw = df_raw.iloc[5].tolist()
    
    # 2. Przygotowanie danych do Mapy Ciepła
    # Wydziały są w kolumnie 0 (od wiersza 7)
    # Wady są w kolumnach od 11 do przedostatniej
    
    wydzialy = df_raw.iloc[7:, 0].ffill()
    wady_df = df_raw.iloc[7:, 11:-1].copy()
    
    # Nadajemy unikalne nazwy kolumnom (na wypadek duplikatów w nagłówkach)
    new_cols = []
    seen = {}
    for i in range(11, df_raw.shape[1] - 1):
        name = str(headers_raw[i])
        if name in seen:
            seen[name] += 1
            new_cols.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 0
            new_cols.append(name)
            
    wady_df.columns = new_cols
    wady_df['Wydzial'] = wydzialy
    
    # Czyszczenie: usuwamy wiersze podsumowań
    mask_to_keep = ~wady_df['Wydzial'].str.contains('Suma|ogólna', case=False, na=False)
    filtered_data = wady_df[mask_to_keep].copy()
    
    # Konwersja danych wad na liczby - bezpieczna metoda dla każdej kolumny po indeksie
    for col_name in new_cols:
        filtered_data[col_name] = pd.to_numeric(filtered_data[col_name], errors='coerce').fillna(0)
            
    # Agregacja po Wydziale
    heatmap_data = filtered_data.groupby('Wydzial').sum()
    
    # Usuwamy kolumny, które mają same zera (brak danej wady w marcu)
    heatmap_data = heatmap_data.loc[:, (heatmap_data != 0).any(axis=0)]
    
    # 3. WIZUALIZACJA (Matplotlib imshow jako zamiennik seaborn heatmap)
    plt.figure(figsize=(16, 10))
    data_values = heatmap_data.values
    
    im = plt.imshow(data_values, cmap='YlOrRd', aspect='auto')
    
    # Dodanie legendy kolorów
    cbar = plt.colorbar(im)
    cbar.set_label('Ilość wad')
    
    # Ustawienie osi
    plt.xticks(range(len(heatmap_data.columns)), heatmap_data.columns, rotation=45, ha='right', fontsize=8)
    plt.yticks(range(len(heatmap_data.index)), heatmap_data.index)
    
    plt.title('MAPA CIEPŁA: Rodzaje Wad vs. Wydziały (Marzec 2026)', fontsize=16, pad=20)
    plt.xlabel('Rodzaj Wady', fontsize=12)
    plt.ylabel('Wydział', fontsize=12)
    
    # Dodanie wartości liczbowych w komórkach (opcjonalnie, tylko dla czytelności)
    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):
            val = data_values[i, j]
            if val > 0:
                text_color = 'white' if val > data_values.max()/2 else 'black'
                plt.text(j, i, int(val), ha='center', va='center', color=text_color, fontsize=8)
    
    plt.tight_layout()
    
    # Zapis
    plot_dir = os.path.join(output_dir, 'propozycje_wizualizacji')
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
        
    plot_path = os.path.join(plot_dir, 'heatmap_wad_polskone.png')
    plt.savefig(plot_path)
    print(f"SUKCES! Mapa ciepła została zapisana jako: {plot_path}")
    
except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
