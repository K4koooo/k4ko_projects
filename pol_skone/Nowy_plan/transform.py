import pandas as pd
import numpy as np

# 1. Wczytanie pliku - pomijamy pierwsze 5 wierszy nagłówkowych, które robią "bałagan"
file_path = "raport wad marzec 2026 - katalog.xlsx"
df = pd.read_excel(file_path, sheet_name=0, header=None)

# 2. Wyciągnięcie prawdziwych nazw kolumn z wiersza nr 5 (indeks 5)
wady_kolumny = df.iloc[5, 13:-1].values # Wady zaczynają się od kolumny 13 do przedostatniej
# Kolumny 0, 8, 11 przechowują odpowiednio Wydział, Kierunek i Grupę ogólną

# Ograniczenie DataFrame tylko do wierszy z danymi (od wiersza 7 w dół) i nadanie tymczasowych nazw kolumn
df_data = df.iloc[7:].copy()

# 3. Przypisywanie informacji z kolumn "wielopoziomowych" (Z uwagi na scalone komórki w Excelu)
# Wyciągamy Wydział (kolumna 0), Kierunek (kolumna 8), Grupa ogólna (kolumna 11)
df_data['Wydział'] = df_data[0]
df_data['Kierunek'] = df_data[8]
df_data['Grupa ogólna'] = df_data[11]

# Uzupełnianie pustych komórek (NaN) wartością z wiersza wyżej (tzw. "wypełnianie w dół" - ffill), 
# co jest standardowym zabiegiem przy tabelach przestawnych z Excela
df_data['Wydział'] = df_data['Wydział'].ffill()
df_data['Kierunek'] = df_data['Kierunek'].ffill()
df_data['Grupa ogólna'] = df_data['Grupa ogólna'].ffill()

# 4. Wyodrębnienie części tabeli, w której zawarte są ilości poszczególnych wad
df_wady = df_data.iloc[:, 13:13+len(wady_kolumny)].copy()
df_wady.columns = wady_kolumny # Przypisanie prawidłowych nagłówków wad

# 5. Złączenie opisów (Wydział, Kierunek, Grupa) z matrycą ilości wad
df_cleaned = pd.concat([df_data[['Wydział', 'Kierunek', 'Grupa ogólna']], df_wady], axis=1)

# 6. Transformacja danych z formatu "szerokiego" na "długi" - operacja MELT
# Dzięki temu uzyskamy kolumny 'Wada' i 'Ilość'
df_long = pd.melt(
    df_cleaned, 
    id_vars=['Wydział', 'Kierunek', 'Grupa ogólna'], # Kolumny, które zostają bez zmian
    var_name='Wada',                                 # Nowa kolumna przechowująca nazwy dawnych kolumn z wadami
    value_name='Ilość'                               # Nowa kolumna przechowująca wartości liczbowe
)

# 7. Czyszczenie wyników końcowych
# Usuwamy wiersze, gdzie Ilość jest pusta (NaN) lub równa 0 - interesują nas tylko rzeczywiste zgłoszenia
df_long = df_long.dropna(subset=['Ilość'])
# Usuwamy stringi itp z kolumny Ilosc zeby mozna bylo castowac na int
df_long['Ilość'] = pd.to_numeric(df_long['Ilość'], errors='coerce')
df_long = df_long.dropna(subset=['Ilość'])
df_long = df_long[df_long['Ilość'] > 0]

df_long['Ilość'] = df_long['Ilość'].astype(int) # Ustawienie typu całkowitego

# (Opcjonalnie) Resetowanie indeksu dla estetyki
df_long = df_long.reset_index(drop=True)

# 8. Zapis gotowego pliku pod Power BI/Tableau
output_file = "raport_wad_do_PowerBI.xlsx"
df_long.to_excel(output_file, index=False)

print(f"Transformacja zakończona! Dane zostały zapisane w strukturze 'długiej' do pliku: {output_file}")
print("\nPodgląd przetworzonych danych:")
print(df_long.head())
