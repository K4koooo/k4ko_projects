import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'
output_dir = r'C:\Users\anton\gemini_cli\pol_skone\propozycje_wizualizacji'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Mapowanie wad na kategorie (te same co wcześniej dla spójności)
category_map = {
    'Błąd produkcji': 'Błędy Prod.',
    'Niezgodność z zamówieniem': 'Błędy Prod.',
    'Brak w dostawie': 'Błędy Prod.',
    'Uszkodzenia mechaniczne': 'Uszkodzenia Mech.',
    'Uszkodzenia mechanczne': 'Uszkodzenia Mech.',
    'Wada konstrukcji': 'Konstrukcja',
    'Wada okuć': 'Okucia',
    'Wada powierzchni': 'Powierzchnia',
}

def get_category(name):
    for key, val in category_map.items():
        if key.lower() in name.lower():
            return val
    return 'Inne'

try:
    # 1. Odczyt i przygotowanie danych
    df_raw = pd.read_excel(file_path, header=None)
    headers_raw = df_raw.iloc[5].tolist()
    wydzialy = df_raw.iloc[7:, 0].ffill()
    mask_to_keep = ~wydzialy.str.contains('Suma|ogólna', case=False, na=False)
    filtered_indices = wydzialy[mask_to_keep].index
    
    cat_data = []
    for i in range(11, df_raw.shape[1] - 1):
        v_name = str(headers_raw[i])
        v_category = get_category(v_name)
        v_values = pd.to_numeric(df_raw.iloc[:, i].loc[filtered_indices], errors='coerce').fillna(0)
        temp_df = pd.DataFrame({'Wydzial': wydzialy.loc[filtered_indices], 'Category': v_category, 'Val': v_values})
        cat_data.append(temp_df)
    
    full_cat_df = pd.concat(cat_data)
    pivot_df = full_cat_df.groupby(['Wydzial', 'Category'])['Val'].sum().unstack().fillna(0)
    
    # Wybieramy Top 3 wydziały do porównania
    top_wydzialy = pivot_df.sum(axis=1).sort_values(ascending=False).head(3).index.tolist()
    radar_df = pivot_df.loc[top_wydzialy]

    # 2. WIZUALIZACJA (Radar Chart)
    categories = list(radar_df.columns)
    N = len(categories)
    
    # Kąty dla każdej osi
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1] # Zamknięcie koła
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Rysowanie dla każdego z Top 3 wydziałów
    colors = ['red', 'blue', 'green']
    for i, wydzial in enumerate(top_wydzialy):
        values = radar_df.loc[wydzial].values.flatten().tolist()
        values += values[:1] # Zamknięcie koła
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=wydzial, color=colors[i])
        ax.fill(angles, values, color=colors[i], alpha=0.1)
    
    # Ustawienia osi
    plt.xticks(angles[:-1], categories, size=11, fontweight='bold')
    ax.set_rlabel_position(0)
    plt.yticks(color="grey", size=8)
    
    plt.title('PROFIL WAD (Radar Chart): Top 3 Wydziały (Marzec 2026)', size=18, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.tight_layout()
    
    # Zapis
    plot_path = os.path.join(output_dir, 'radar_wad_polskone.png')
    plt.savefig(plot_path)
    print(f"SUKCES! Wykres radarowy został zapisany jako: {plot_path}")
    
except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
