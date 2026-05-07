import pandas as pd
import matplotlib.pyplot as plt
import os
import math

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'
output_dir = r'C:\Users\anton\gemini_cli\pol_skone\propozycje_wizualizacji'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    # 1. Odczyt i przygotowanie danych
    df_raw = pd.read_excel(file_path, header=None)
    headers_raw = df_raw.iloc[5].tolist()
    wydzialy = df_raw.iloc[7:, 0].ffill()
    
    # Czyszczenie: usuwamy wiersze podsumowań
    mask_to_keep = ~wydzialy.str.contains('Suma|ogólna', case=False, na=False)
    filtered_indices = wydzialy[mask_to_keep].index
    
    # Przygotowanie "długiego" formatu danych
    long_data = []
    for i in range(11, df_raw.shape[1] - 1):
        v_name = str(headers_raw[i])
        v_values = pd.to_numeric(df_raw.iloc[:, i].loc[filtered_indices], errors='coerce').fillna(0)
        temp_df = pd.DataFrame({
            'Wydzial': wydzialy.loc[filtered_indices],
            'Wada': v_name,
            'Ilosc': v_values
        })
        long_data.append(temp_df)
    
    df_long = pd.concat(long_data)
    df_grouped = df_long.groupby(['Wydzial', 'Wada'])['Ilosc'].sum().reset_index()
    
    # Filtrujemy tylko wydziały z wadami
    active_wydzialy = df_grouped.groupby('Wydzial')['Ilosc'].sum().sort_values(ascending=False)
    active_wydzialy = active_wydzialy[active_wydzialy > 0].index.tolist()

    # 2. WIZUALIZACJA (Trellis Chart)
    n_wydz = len(active_wydzialy)
    cols = 2
    rows = math.ceil(n_wydz / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(20, 6 * rows))
    axes = axes.flatten()
    plt.style.use('bmh')

    for i, wydzial in enumerate(active_wydzialy):
        ax = axes[i]
        # Pobieramy Top 5 wad dla danego wydziału
        top_wady = df_grouped[df_grouped['Wydzial'] == wydzial].sort_values('Ilosc', ascending=False).head(5)
        
        # Skracanie nazw wad dla czytelności
        short_names = [n[:45] + '...' if len(str(n)) > 45 else n for n in top_wady['Wada']]
        
        bars = ax.barh(short_names, top_wady['Ilosc'], color='indianred', alpha=0.8)
        ax.set_title(f'Wydział: {wydzial}', fontsize=16, fontweight='bold', color='darkslategray')
        ax.invert_yaxis()
        ax.set_xlabel('Ilość wad')
        
        # Dodanie wartości na słupkach
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center', fontsize=10)

    # Ukrywamy puste podwykresy
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.suptitle('TOP 5 PRZYCZYN REKLAMACJI DLA KAŻDEGO WYDZIAŁU (Marzec 2026)', fontsize=22, y=1.02)
    plt.tight_layout()
    
    # Zapis
    plot_path = os.path.join(output_dir, 'trellis_top_wady_polskone.png')
    plt.savefig(plot_path)
    print(f"SUKCES! Wykres Trellis został zapisany jako: {plot_path}")
    
except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
