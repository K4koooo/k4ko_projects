import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'
output_dir = r'C:\Users\anton\gemini_cli\pol_skone\propozycje_wizualizacji'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    # 1. Odczyt danych
    df_raw = pd.read_excel(file_path, header=None)
    
    # 2. Przygotowanie danych (Agregacja po Wydziale)
    # Wydział w kolumnie 0, Suma w ostatniej kolumnie
    clean_data = pd.DataFrame()
    clean_data['Wydzial'] = df_raw.iloc[7:, 0].ffill()
    clean_data['Suma'] = pd.to_numeric(df_raw.iloc[7:, -1], errors='coerce').fillna(0)
    
    # Czyszczenie: usuwamy wiersze podsumowań
    mask_to_keep = ~clean_data['Wydzial'].str.contains('Suma|ogólna', case=False, na=False)
    filtered_data = clean_data[mask_to_keep].copy()
    
    # Agregacja
    stats_wydzial = filtered_data.groupby('Wydzial')['Suma'].sum().sort_values(ascending=False)
    
    # Usuwamy wydziały z zerową sumą wad
    stats_wydzial = stats_wydzial[stats_wydzial > 0]

    # 3. WIZUALIZACJA
    plt.figure(figsize=(12, 10))
    plt.style.use('ggplot')

    # Kolory
    colors = plt.cm.Paired(range(len(stats_wydzial)))

    # Wykres kołowy
    wedges, texts, autotexts = plt.pie(
        stats_wydzial, 
        labels=stats_wydzial.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        pctdistance=0.85,
        explode=[0.05] * len(stats_wydzial) # Lekkie wysunięcie kawałków
    )

    # Rysowanie białego koła w środku (efekt Donut)
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # Stylizacja tekstów
    plt.setp(autotexts, size=10, weight="bold", color="black")
    plt.setp(texts, size=12)

    plt.title('STRUKTURA REKLAMACJI: Udział Wydziałów (Marzec 2026)', fontsize=18, pad=20)
    plt.axis('equal') # Zapewnia, że wykres jest kołem

    plt.tight_layout()
    
    # Zapis
    plot_path = os.path.join(output_dir, 'donut_wad_polskone.png')
    plt.savefig(plot_path)
    print(f"SUKCES! Wykres pierścieniowy został zapisany jako: {plot_path}")
    
except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
