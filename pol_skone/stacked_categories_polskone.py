import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'
output_dir = r'C:\Users\anton\gemini_cli\pol_skone\propozycje_wizualizacji'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Mapowanie wad na kategorie
category_map = {
    'Błąd produkcji': 'Błędy Prod./Konfig.',
    'Niezgodność z zamówieniem': 'Błędy Prod./Konfig.',
    'Brak w dostawie': 'Błędy Prod./Konfig.',
    'Uszkodzenia mechaniczne': 'Uszkodzenia Mech.',
    'Uszkodzenia mechanczne': 'Uszkodzenia Mech.',
    'Wada konstrukcji': 'Wady Konstrukcyjne',
    'Wada okuć': 'Wady Okuć',
    'Wada powierzchni': 'Wady Powierzchniowe',
}

def get_category(name):
    for key, val in category_map.items():
        if key.lower() in name.lower():
            return val
    return 'Inne'

try:
    # 1. Odczyt danych
    df_raw = pd.read_excel(file_path, header=None)
    headers_raw = df_raw.iloc[5].tolist()
    
    # 2. Przygotowanie danych
    wydzialy = df_raw.iloc[7:, 0].ffill()
    wady_df = df_raw.iloc[7:, 11:-1].copy()
    
    # Czyszczenie: usuwamy wiersze podsumowań
    mask_to_keep = ~wydzialy.str.contains('Suma|ogólna', case=False, na=False)
    filtered_indices = wydzialy[mask_to_keep].index
    
    # Zbieranie danych do kategorii
    cat_data = []
    for i in range(11, df_raw.shape[1] - 1):
        v_name = str(headers_raw[i])
        v_category = get_category(v_name)
        v_values = pd.to_numeric(df_raw.iloc[:, i].loc[filtered_indices], errors='coerce').fillna(0)
        
        temp_df = pd.DataFrame({
            'Wydzial': wydzialy.loc[filtered_indices],
            'Category': v_category,
            'Val': v_values
        })
        cat_data.append(temp_df)
    
    # Łączenie i agregacja
    full_cat_df = pd.concat(cat_data)
    final_pivot = full_cat_df.groupby(['Wydzial', 'Category'])['Val'].sum().unstack().fillna(0)
    
    # Sortowanie wydziałów po całkowitej sumie wad
    final_pivot['Total'] = final_pivot.sum(axis=1)
    final_pivot = final_pivot.sort_values('Total', ascending=False).drop(columns='Total')
    
    # Usuwamy wydziały z zerową sumą
    final_pivot = final_pivot[final_pivot.sum(axis=1) > 0]

    # 3. WIZUALIZACJA
    ax = final_pivot.plot(kind='bar', stacked=True, figsize=(15, 10), colormap='viridis')
    
    plt.title('STRUKTURA WAD NA WYDZIAŁACH: Analiza Kategorii (Marzec 2026)', fontsize=18, pad=20)
    plt.xlabel('Wydział', fontsize=12, fontweight='bold')
    plt.ylabel('Łączna ilość wad', fontsize=12, fontweight='bold')
    plt.xticks(rotation=0)
    plt.legend(title='Kategoria Wady', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Zapis
    plot_path = os.path.join(output_dir, 'kategorie_wad_polskone.png')
    plt.savefig(plot_path)
    print(f"SUKCES! Wykres skumulowany został zapisany jako: {plot_path}")
    
except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
