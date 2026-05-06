import pandas as pd
import os
import sys

def generate_insights():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Wybór folderu zapisu
    output_dir = sys.argv[1] if len(sys.argv) > 1 else base_dir
    file_path = os.path.join(output_dir, 'raport_clean.csv')
    output_md = os.path.join(output_dir, 'ANALIZA_WNIOSKI.md')

    try:
        df = pd.read_csv(file_path)
        total_wady = df['Ilosc'].sum()
        
        top_wydzialy = df.groupby('Wydzial')['Ilosc'].sum().sort_values(ascending=False)
        top1_wydzial = top_wydzialy.index[0]
        top1_wydzial_val = top_wydzialy.iloc[0]
        top_kategorie = df.groupby('Kategoria')['Ilosc'].sum().sort_values(ascending=False)
        top1_cat = top_kategorie.index[0]
        top_vada = df.groupby('Oryginalna_Wada')['Ilosc'].sum().sort_values(ascending=False).head(1)
        vada_name = top_vada.index[0]
        vada_val = top_vada.iloc[0]

        report = f"""# RAPORT JAKOŚCI POL-SKONE - WNIOSKI

## 1. GŁÓWNE ZAGROŻENIE
- **Wada:** {vada_name}
- **Wpływ:** {round(vada_val/total_wady*100, 1)}% wszystkich reklamacji.
- **Wydział zapalny:** {df[df['Oryginalna_Wada'] == vada_name].groupby('Wydzial')['Ilosc'].sum().idxmax()}

## 2. STATYSTYKA WYDZIAŁÓW
- **Najwięcej wad:** {top1_wydzial} ({top1_wydzial_val} szt.)
- **Kategoria dominująca:** {top1_cat}

---
*Wygenerowano automatycznie w folderze: {output_dir}*
"""
        with open(output_md, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"SUKCES: Raport wniosków zapisany w {output_md}")
        return True
    except Exception as e:
        print(f"BŁĄD: {e}")
        return False

if __name__ == "__main__":
    generate_insights()
