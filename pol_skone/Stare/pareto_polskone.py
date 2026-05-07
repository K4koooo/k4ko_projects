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
    headers_raw = df_raw.iloc[5].tolist()
    
    # 2. Przygotowanie danych (Agregacja Wad)
    wydzialy = df_raw.iloc[7:, 0].ffill()
    wady_df = df_raw.iloc[7:, 11:-1].copy()
    
    # Czyszczenie: usuwamy wiersze podsumowań
    mask_to_keep = ~wydzialy.str.contains('Suma|ogólna', case=False, na=False)
    data_indices = wydzialy[mask_to_keep].index
    
    wady_sum = {}
    for i in range(11, df_raw.shape[1] - 1):
        v_name = str(headers_raw[i])
        v_values = pd.to_numeric(df_raw.iloc[data_indices, i], errors='coerce').fillna(0)
        v_sum = v_values.sum()
        if v_sum > 0:
            wady_sum[v_name] = wady_sum.get(v_name, 0) + v_sum
            
    # Tworzenie DataFrame dla Pareto
    df_pareto = pd.DataFrame.from_dict(wady_sum, orient='index', columns=['Ilosc'])
    df_pareto = df_pareto.sort_values(by='Ilosc', ascending=False)
    
    # Obliczanie procentów
    df_pareto['CumPercentage'] = df_pareto['Ilosc'].cumsum() / df_pareto['Ilosc'].sum() * 100
    
    # 3. WIZUALIZACJA
    fig, ax1 = plt.subplots(figsize=(16, 10))
    plt.style.use('ggplot')

    # Wykres słupkowy (Ilość wad)
    ax1.bar(df_pareto.index, df_pareto['Ilosc'], color='steelblue', alpha=0.8)
    ax1.set_ylabel('Ilość wad', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Rodzaj wady', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45, labelsize=9)
    # Skrócenie długich nazw na osi X
    ax1.set_xticklabels([n[:40] + '...' if len(str(n)) > 40 else n for n in df_pareto.index], ha='right')

    # Druga oś Y dla linii skumulowanej
    ax2 = ax1.twinx()
    ax2.plot(df_pareto.index, df_pareto['CumPercentage'], color='crimson', marker='D', ms=5, lw=2)
    ax2.axhline(80, color='green', linestyle='--', alpha=0.6, label='Próg 80%')
    ax2.set_ylabel('Skumulowany procent (%)', fontsize=12, fontweight='bold', color='crimson')
    ax2.set_ylim(0, 110)
    ax2.grid(None) # Usuwamy siatkę dla drugiej osi, żeby nie nakładała się na pierwszą

    plt.title('ANALIZA PARETO: Przyczyny Reklamacji Pol-Skone (Marzec 2026)', fontsize=18, pad=20)
    
    # Dodanie legendy
    ax2.legend(loc='center right')

    plt.tight_layout()
    
    # Zapis
    plot_path = os.path.join(output_dir, 'pareto_wad_polskone.png')
    plt.savefig(plot_path)
    print(f"SUKCES! Wykres Pareto został zapisany jako: {plot_path}")
    
except Exception as e:
    print(f"Błąd: {e}")
    import traceback
    traceback.print_exc()
