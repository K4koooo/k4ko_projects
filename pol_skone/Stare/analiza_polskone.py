import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'
output_dir = r'C:\Users\anton\gemini_cli\pol_skone'

try:
    # 1. Odczyt danych
    df_raw = pd.read_excel(file_path, header=None)
    headers_raw = df_raw.iloc[5].tolist()
    
    # 2. Przygotowanie czystej tabeli danych
    clean_data = pd.DataFrame()
    clean_data['Wydzial'] = df_raw.iloc[7:, 0].ffill()
    clean_data['Suma'] = pd.to_numeric(df_raw.iloc[7:, -1], errors='coerce').fillna(0)
    
    # DODATKOWE CZYSZCZENIE: Usuwamy wiersze, które są podsumowaniami wewnątrz arkusza
    # (te które mają "Suma" w nazwie wydziału lub są "Sumą ogólną")
    mask_to_keep = ~clean_data['Wydzial'].str.contains('Suma|ogólna', case=False, na=False)
    filtered_data = clean_data[mask_to_keep].copy()
    
    # 3. Agregacja wydziałów (teraz bez duplikatów)
    stats_wydzial = filtered_data.groupby('Wydzial')['Suma'].sum().sort_values(ascending=False)
    
    # 4. Agregacja wad (używając tylko przefiltrowanych wierszy danych)
    wady_sum = {}
    num_cols = df_raw.shape[1]
    data_indices = filtered_data.index
    
    for i in range(11, num_cols - 1):
        v_name = str(headers_raw[i])
        # Liczymy sumę tylko dla wierszy, które nie są podsumowaniami
        v_values = pd.to_numeric(df_raw.iloc[data_indices, i], errors='coerce').fillna(0)
        v_sum = v_values.sum()
        
        if v_sum > 0:
            if v_name in wady_sum:
                wady_sum[v_name] += v_sum
            else:
                wady_sum[v_name] = v_sum
                
    stats_wady = pd.Series(wady_sum).sort_values(ascending=False)
    
    # 5. WYKRESY
    plt.style.use('ggplot')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 16))
    
    # Wykres Wydziałów
    stats_wydzial.plot(kind='bar', ax=ax1, color='teal')
    ax1.set_title('Poprawiona Suma wad na Wydział (Marzec 2026)', fontsize=16)
    ax1.set_ylabel('Ilość')
    ax1.tick_params(axis='x', rotation=0)
    
    # Wykres Wad
    top_wady = stats_wady.head(10)
    short_names = [n[:50] + '...' if len(str(n)) > 50 else n for n in top_wady.index]
    top_wady.index = short_names
    top_wady.plot(kind='barh', ax=ax2, color='coral')
    ax2.set_title('Top 10 Przyczyn Reklamacji - Analiza Pareto', fontsize=16)
    ax2.set_xlabel('Ilość')
    ax2.invert_yaxis()
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'wizualizacja_wad_CZYSTA.png')
    plt.savefig(plot_path)
    
    print(f"SUKCES! Czysta wizualizacja zapisana jako: {plot_path}")
    print("\n--- POPRAWIONE STATYSTYKI WYDZIAŁÓW ---")
    print(stats_wydzial)
    print("\n--- TOP 5 WAD ---")
    print(stats_wady.head(5))

except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
