import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def generate_dashboard():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Wybór folderu zapisu
    output_dir = sys.argv[1] if len(sys.argv) > 1 else base_dir
    file_path = os.path.join(output_dir, 'raport_clean.csv')

    try:
        df = pd.read_csv(file_path)
        plt.style.use('ggplot')

        # 1. Kategorie
        plt.figure(figsize=(10, 8))
        df.groupby('Kategoria')['Ilosc'].sum().plot(kind='pie', autopct='%1.1f%%')
        plt.title('STRUKTURA WAD')
        plt.savefig(os.path.join(output_dir, '01_kategorie.png'))
        plt.close()

        # 2. Pareto
        plt.figure(figsize=(12, 8))
        df.groupby('Oryginalna_Wada')['Ilosc'].sum().sort_values(ascending=False).head(10).plot(kind='bar', color='coral')
        plt.title('TOP 10 WAD')
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '02_pareto.png'))
        plt.close()

        print(f"SUKCES: Dashboard zapisany w {output_dir}")
        return True
    except Exception as e:
        print(f"BŁĄD: {e}")
        return False

if __name__ == "__main__":
    generate_dashboard()
