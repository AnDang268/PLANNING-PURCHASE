try:
    import openpyxl
    print("openpyxl: INSTALLED")
except ImportError:
    print("openpyxl: MISSING")

try:
    import xlrd
    print("xlrd: INSTALLED")
except ImportError:
    print("xlrd: MISSING")
