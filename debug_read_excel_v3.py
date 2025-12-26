
import pandas as pd

file_path = r"d:\Document\SOURCE\PLANNING-PURCHASE\doc\So_chi_tiet_ban_hang.xlsx"

try:
    # Read first 10 rows as raw data
    df = pd.read_excel(file_path, header=None, nrows=10)
    print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
