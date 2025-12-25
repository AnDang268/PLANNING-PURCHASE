
import pandas as pd
import json

def inspect_excel_refined():
    file_path = r"d:\Document\SOURCE\PLANNING-PURCHASE\doc\XNT - WIN GỐI_Update 14.12.2025.xlsx"
    sheets_to_check = ['WEEK', 'ORDER']
    
    analysis = {}
    
    try:
        for sheet in sheets_to_check:
            print(f"Reading Sheet: {sheet}...")
            # Read first few rows to find the header row. 
            # Often headers in complex excels are not in row 0. 
            # We'll read 10 rows and look for a row that has 'Mã hàng' or 'SKU'
            df = pd.read_excel(file_path, sheet_name=sheet, header=None, nrows=10)
            
            # Simple heuristic: The row with the most non-null values is likely the header
            header_row_idx = 0
            max_non_null = 0
            
            for i in range(len(df)):
                non_null = df.iloc[i].count()
                if non_null > max_non_null:
                    max_non_null = non_null
                    header_row_idx = i
            
            print(f"Detected Header at Row: {header_row_idx}")
            
            # Re-read with correct header
            df_cleaned = pd.read_excel(file_path, sheet_name=sheet, header=header_row_idx, nrows=0)
            columns = list(df_cleaned.columns)
            
            # Clean column names (strip newlines)
            columns = [str(c).replace('\n', ' ').strip() for c in columns]
            analysis[sheet] = columns
            
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    inspect_excel_refined()
