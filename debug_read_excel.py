
import pandas as pd
import os

file_path = r"d:\Document\SOURCE\PLANNING-PURCHASE\doc\So_chi_tiet_ban_hang.xlsx"

try:
    df = pd.read_excel(file_path, nrows=10)
    print("Columns:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head(5).to_string())
except Exception as e:
    print(f"Error reading excel: {e}")
