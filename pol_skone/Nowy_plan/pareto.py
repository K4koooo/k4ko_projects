import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# 1. Wczytanie danych
file_path = "raport_wad_do_PowerBI.xlsx"
df = pd.read_excel(file_path)

# 2. Agregacja danych - sumujemy ilości dla każdej kategorii wad
df_agg = df.groupby('Wada')['Ilość'].sum().reset_index()

# 3. Sortowanie malejąco
df_agg = df_agg.sort_values(by='Ilość', ascending=False)

# 4. Obliczenie skumulowanego procentu
df_agg['Skumulowany_procent'] = df_agg['Ilość'].cumsum() / df_agg['Ilość'].sum() * 100

# 5. Tworzenie wykresu
fig, ax1 = plt.subplots(figsize=(14, 8))

# Wykres słupkowy (Ilość) na głównej osi Y
color = 'tab:blue'
ax1.set_xlabel('Kategoria wady (Wada)', fontsize=12)
ax1.set_ylabel('Ilość zgłoszeń', color=color, fontsize=12)
ax1.bar(df_agg['Wada'], df_agg['Ilość'], color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.tick_params(axis='x', rotation=45, labelsize=10)

# Ustawienie etykiet na osi X, aby były czytelne
plt.xticks(rotation=75, ha='right')

# Druga oś Y dla skumulowanego procentu
ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Skumulowany procent (%)', color=color, fontsize=12)  
ax2.plot(df_agg['Wada'], df_agg['Skumulowany_procent'], color=color, marker='o', linestyle='-', linewidth=2)
ax2.tick_params(axis='y', labelcolor=color)
# Ustawiamy skalę od 0 do 105% dla przejrzystości
ax2.set_ylim([0, 105])
ax2.yaxis.set_major_formatter(PercentFormatter())

# Linia 80% zasady Pareto (wskazuje, które wady generują 80% problemów)
ax2.axhline(80, color='gray', linestyle='dashed', alpha=0.7)
ax2.text(len(df_agg)*0.95, 82, 'Zasada 80%', color='gray', va='bottom', ha='right')

# Tytuł i układ
plt.title('Wykres Pareto dla zgłoszeń wad (marzec 2026)', fontsize=16, fontweight='bold')
plt.tight_layout()

# 6. Zapis wykresu
output_image = "pareto_chart.png"
plt.savefig(output_image, dpi=300)
print(f"Wykres został wygenerowany i zapisany jako: {output_image}")
