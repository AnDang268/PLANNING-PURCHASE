
import pandas as pd

file_path = r"d:\Document\SOURCE\PLANNING-PURCHASE\doc\So_chi_tiet_ban_hang.xlsx"

try:
    # Try reading with header at row 3 (index 2)
    df = pd.read_excel(file_path, header=2, nrows=5)
    print("--- Header Row 2 ---")
    print(df.columns.tolist())
    print(df.head(2).to_string())
    
    # Try reading with header at row 8 (index 7) - sometimes headers are lower
    df2 = pd.read_excel(file_path, header=7, nrows=5)
    print("\n--- Header Row 7 ---")
    print(df2.columns.tolist())
    print(df2.head(2).to_string())

except Exception as e:
    print(f"Error: {e}")
