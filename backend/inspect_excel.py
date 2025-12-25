
import pandas as pd

def inspect_excel():
    file_path = r"d:\Document\SOURCE\PLANNING-PURCHASE\doc\XNT - WIN GỐI_Update 14.12.2025.xlsx"
    try:
        xl = pd.ExcelFile(file_path)
        print("Sheet Names:", xl.sheet_names)
        
        for sheet in xl.sheet_names:
            print(f"\n--- SHEET: {sheet} ---")
            df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
            print(df.head())
            print("Columns:", list(df.columns))
            
    except Exception as e:
        print("Error reading Excel:", e)

if __name__ == "__main__":
    inspect_excel()
