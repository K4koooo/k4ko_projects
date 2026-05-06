import pandas as pd
import os

def create_variant(name):
    source_file = r'C:\Users\anton\gemini_cli\pol_skone\Generator_raportów\Pliki_do_analizy\raport wad marzec 2026 - katalog.xls'
    output_file = os.path.join(r'C:\Users\anton\gemini_cli', f'raport_{name}.xlsx')

    try:
        df = pd.read_excel(source_file, header=None)
        
        # Konwertujemy cały DataFrame na typ object, aby uniknąć błędów typowania
        df = df.astype(object)
        
        # Zerujemy dane (kolumny 11 do końca-1, wiersze od 7)
        for r in range(7, df.shape[0]):
            for c in range(11, df.shape[1] - 1):
                df.iloc[r, c] = 0

        if name == 'a':
            df.iloc[7, 11+19] = 1234 # Top wada dla Z1WD
        elif name == 'b':
            df.iloc[20, 11+25] = 5678 # Top wada dla Z4WF
        elif name == 'c':
            df.iloc[10, 11+12] = 999  # Top wada Logistyka

        df.to_excel(output_file, index=False, header=False)
        print(f"UTWORZONO: {output_file}")

    except Exception as e:
        print(f"BŁĄD {name}: {e}")

if __name__ == "__main__":
    create_variant('a')
    create_variant('b')
    create_variant('c')
