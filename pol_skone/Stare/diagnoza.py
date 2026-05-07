import pandas as pd
import sys

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'

try:
    # Próba odczytu arkusza
    df = pd.read_excel(file_path)
    print("Nagłówki kolumn:")
    print(df.columns.tolist())
    print("\nPierwsze 5 wierszy:")
    print(df.head())
except Exception as e:
    print(f"Błąd podczas odczytu pliku: {e}")
