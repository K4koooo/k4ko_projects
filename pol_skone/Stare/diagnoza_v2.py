import pandas as pd

file_path = r'C:\Users\anton\gemini_cli\pol_skone\raport wad marzec 2026 - katalog.xls'

try:
    xl = pd.ExcelFile(file_path)
    print(f"Arkusze: {xl.sheet_names}")
    
    # Czytamy pierwszy arkusz bez skipowania czegokolwiek
    df_raw = pd.read_excel(file_path, sheet_name=xl.sheet_names[0], header=None)
    print("\nSurowe pierwsze 10 wierszy:")
    print(df_raw.head(10).to_string())
except Exception as e:
    print(f"Błąd: {e}")
