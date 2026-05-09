import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import squarify

# Set paths
data_path = "c:/Code_Antigravity/k4ko_projects/pol_skone/Nowy_plan/raport wad marzec 2026 - katalog_PowerBI.xlsx"
output_dir = "c:/Code_Antigravity/k4ko_projects/pol_skone/Nowy_plan"

# Load data
df = pd.read_excel(data_path)

# Ensure columns exist, if not, print error and exit
expected_cols = ['Wydział', 'Kierunek', 'Grupa ogólna', 'Wada', 'Ilość']
for col in expected_cols:
    if col not in df.columns:
        print(f"Missing column: {col}")
        
# Fill NaNs
df['Ilość'] = pd.to_numeric(df['Ilość'], errors='coerce').fillna(0)

# Set style
plt.style.use('dark_background')
plt.rcParams['font.size'] = 10

# ---------------------------------------------------------
# Dashboard 1: Executive Quality Overview
# ---------------------------------------------------------
fig1 = plt.figure(figsize=(16, 10))
fig1.suptitle("Dashboard 1: Executive Quality Overview", fontsize=24, color='white', y=0.98)

# 1. KPI Card (Text)
ax1 = plt.subplot(2, 2, 1)
ax1.axis('off')
total_defects = int(df['Ilość'].sum())
ax1.text(0.5, 0.5, f"Total Defects\n{total_defects:,}", ha='center', va='center', fontsize=48, color='#4CAF50', weight='bold')

# 2. Donut Chart (Kierunek)
ax2 = plt.subplot(2, 2, 2)
kierunek_data = df.groupby('Kierunek')['Ilość'].sum()
ax2.pie(kierunek_data, labels=kierunek_data.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'], textprops={'color':"w", 'fontsize': 14})
centre_circle = plt.Circle((0,0),0.70,fc='black') # Using black for dark background
ax2.add_artist(centre_circle)
ax2.set_title('Defects by Direction (PL vs EX)', fontsize=16)

# 3. Stacked Column Chart (Wydział vs Ilość by Grupa ogólna)
ax3 = plt.subplot(2, 2, 3)
pivot_wydzial = df.pivot_table(index='Wydział', columns='Grupa ogólna', values='Ilość', aggfunc='sum').fillna(0)
pivot_wydzial.plot(kind='bar', stacked=True, ax=ax3, colormap='viridis')
ax3.set_title('Defects by Department and Category', fontsize=16)
ax3.set_ylabel('Total Defects')
ax3.tick_params(axis='x', rotation=45)
ax3.legend(title='Grupa ogólna', facecolor='#2e2e2e', edgecolor='white')

# 4. Treemap (Wada)
ax4 = plt.subplot(2, 2, 4)
wada_data = df.groupby('Wada')['Ilość'].sum().sort_values(ascending=False).head(10) # Top 10

squarify.plot(sizes=wada_data.values, label=wada_data.index, alpha=0.8, ax=ax4, text_kwargs={'fontsize':10, 'color':'black', 'weight':'bold'})
ax4.axis('off')
ax4.set_title('Top 10 Defects (Treemap)', fontsize=16)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
fig1.savefig(os.path.join(output_dir, "dash_Executive_Quality_Overview.png"), facecolor='black')
plt.close(fig1)

# ---------------------------------------------------------
# Dashboard 2: Production Quality Control
# ---------------------------------------------------------
fig2 = plt.figure(figsize=(16, 10))
fig2.suptitle("Dashboard 2: Production Quality Control", fontsize=24, color='white', y=0.98)

# 1. Pareto Chart (Wada)
ax1 = plt.subplot(2, 1, 1)
wada_pareto = df.groupby('Wada')['Ilość'].sum().sort_values(ascending=False)
wada_pareto = wada_pareto[wada_pareto > 0] # non zero
if len(wada_pareto) > 30:
    wada_pareto = wada_pareto.head(30) # Limit to 30 for visibility
cum_perc = wada_pareto.cumsum() / wada_pareto.sum() * 100

ax1.bar(wada_pareto.index, wada_pareto.values, color='steelblue')
ax1_twin = ax1.twinx()
ax1_twin.plot(wada_pareto.index, cum_perc.values, color='red', marker='D', ms=5)
ax1_twin.axhline(80, color='orange', linestyle='dashed', alpha=0.7)
ax1.set_xticks(range(len(wada_pareto.index)))
ax1.set_xticklabels(wada_pareto.index, rotation=45, ha='right', fontsize=9)
ax1.set_title('Pareto Chart of Defects (Top 30)', fontsize=16)
ax1.set_ylabel('Count', color='steelblue')
ax1_twin.set_ylabel('Cumulative Percentage (%)', color='red')
ax1.grid(False)
ax1_twin.grid(False)

# 2. Heatmap (Wydział vs Wada)
ax2 = plt.subplot(2, 1, 2)
heatmap_data = df.pivot_table(index='Wydział', columns='Wada', values='Ilość', aggfunc='sum').fillna(0)
# Select top 20 defects for readability
top_wada_cols = heatmap_data.sum().sort_values(ascending=False).head(20).index
heatmap_data = heatmap_data[top_wada_cols]

cax = ax2.imshow(heatmap_data, cmap='hot', aspect='auto')
plt.colorbar(cax, ax=ax2, label='Ilość')
ax2.set_xticks(np.arange(len(heatmap_data.columns)))
ax2.set_yticks(np.arange(len(heatmap_data.index)))
ax2.set_xticklabels(heatmap_data.columns, rotation=45, ha='right', fontsize=9)
ax2.set_yticklabels(heatmap_data.index)

# Add text annotations
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        val = int(heatmap_data.values[i, j])
        if val > 0:
            ax2.text(j, i, val, ha="center", va="center", color="w", fontsize=8)

ax2.set_title('Heatmap: Department vs Top 20 Defects', fontsize=16)
ax2.grid(False)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
fig2.savefig(os.path.join(output_dir, "dash_Production_Quality_Control.png"), facecolor='black')
plt.close(fig2)


# ---------------------------------------------------------
# Dashboard 3: Cross-Analysis: Market vs. Defect
# ---------------------------------------------------------
fig3 = plt.figure(figsize=(16, 10))
fig3.suptitle("Dashboard 3: Cross-Analysis: Market vs. Defect", fontsize=24, color='white', y=0.98)

# 1. Tornado Chart (PL vs EX)
ax1 = plt.subplot(1, 2, 1)
pivot_kierunek = df.pivot_table(index='Wada', columns='Kierunek', values='Ilość', aggfunc='sum').fillna(0)

# Check if PL and EX exist, handle gracefully if different names
pl_col = 'PL' if 'PL' in pivot_kierunek.columns else (pivot_kierunek.columns[0] if len(pivot_kierunek.columns) > 0 else 'PL')
ex_col = 'EX' if 'EX' in pivot_kierunek.columns else (pivot_kierunek.columns[-1] if len(pivot_kierunek.columns) > 1 else 'EX')

if pl_col in pivot_kierunek.columns and ex_col in pivot_kierunek.columns:
    # Top 20 overall
    top_wada = pivot_kierunek.sum(axis=1).sort_values(ascending=False).head(20).index
    pivot_kierunek = pivot_kierunek.loc[top_wada]

    y_pos = np.arange(len(pivot_kierunek))

    ax1.barh(y_pos, -pivot_kierunek[pl_col], align='center', color='#ff9999', label=pl_col)
    ax1.barh(y_pos, pivot_kierunek[ex_col], align='center', color='#66b3ff', label=ex_col)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(pivot_kierunek.index)
    ax1.invert_yaxis()  # labels read top-to-bottom
    ax1.set_xlabel('Ilość')
    ax1.set_title(f'Tornado Chart: {pl_col} vs {ex_col} by Defect', fontsize=16)
    ax1.legend()
    
    # Format x ticks to be positive
    import matplotlib.ticker as ticker
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(abs(x))}"))

else:
    ax1.text(0.5, 0.5, "Insufficient direction data", ha='center', va='center')

# 2. Key Influencers (Top Wadas by Kierunek)
ax2 = plt.subplot(1, 2, 2)
ax2.axis('off')
ax2.set_title("Key Insights", fontsize=16)

if pl_col in pivot_kierunek.columns and ex_col in pivot_kierunek.columns:
    pl_total = df[df['Kierunek'] == pl_col]['Ilość'].sum()
    ex_total = df[df['Kierunek'] == ex_col]['Ilość'].sum()
    pl_top = pivot_kierunek[pl_col].idxmax() if pl_total > 0 else "None"
    ex_top = pivot_kierunek[ex_col].idxmax() if ex_total > 0 else "None"
    
    insights = [
        f"Rynek Krajowy ({pl_col}):",
        f"- Całkowita liczba wad: {int(pl_total):,}",
        f"- Najczęstsza wada: {pl_top} ({int(pivot_kierunek[pl_col].max())})",
        "",
        f"Rynek Eksportowy ({ex_col}):",
        f"- Całkowita liczba wad: {int(ex_total):,}",
        f"- Najczęstsza wada: {ex_top} ({int(pivot_kierunek[ex_col].max())})",
    ]
else:
    insights = ["Brak danych do porównania rynków."]

for i, insight in enumerate(insights):
    ax2.text(0.1, 0.8 - i*0.05, insight, fontsize=16, color='lightgreen' if insight.startswith('-') else 'white', weight='bold' if not insight.startswith('-') else 'normal')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
fig3.savefig(os.path.join(output_dir, "dash_Cross_Analysis.png"), facecolor='black')
plt.close(fig3)

print("Dashboards generated successfully!")
