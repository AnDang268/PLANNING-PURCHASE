import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import DimProducts, DimCustomers, DimVendors, FactSales, SystemSyncLogs

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_from_excel(self, file_path, entity_type):
        """
        Generic Import Function.
        entity_type: 'product', 'customer', 'vendor', 'sales'
        Excel columns must match logic.
        Expected 'Action' column: 'NEW', 'UPDATE', 'DELETE' (Default to UPSERT if empty)
        """
        start_time = datetime.now()
        log = SystemSyncLogs(source='EXCEL', action_type=f'IMPORT_{entity_type.upper()}', status='RUNNING', start_time=start_time)
        self.db.add(log)
        self.db.commit()

        try:
            df = pd.read_excel(file_path)
            df.columns = [c.strip().upper() for c in df.columns] # Normalize headers
            
            count = 0
            for _, row in df.iterrows():
                action = row.get('ACTION', 'UPSERT').upper()
                
                if entity_type == 'product':
                    self._process_product(row, action)
                elif entity_type == 'sales':
                    self._process_sales(row, action)
                elif entity_type == 'customer':
                    self._process_customer(row, action)
                elif entity_type == 'vendor':
                    self._process_vendor(row, action)
                
                count += 1
            
            log.status = 'SUCCESS'
            log.records_processed = count
            log.end_time = datetime.now()
            self.db.commit()
            return {"status": "success", "count": count}

        except Exception as e:
            log.status = 'ERROR'
            log.error_message = str(e)
            log.end_time = datetime.now()
            self.db.commit()
            raise e

    def _process_product(self, row, action):
        sku = str(row['SKU_ID'])
        existing = self.db.query(DimProducts).filter(DimProducts.sku_id == sku).first()

        if action == 'DELETE':
            if existing: self.db.delete(existing)
        else:
            # Upsert
            if existing:
                existing.product_name = row.get('PRODUCT_NAME', existing.product_name)
                existing.category = row.get('CATEGORY', existing.category)
                existing.min_stock_level = row.get('MIN_STOCK', existing.min_stock_level)
            else:
                new_item = DimProducts(
                    sku_id=sku,
                    product_name=row.get('PRODUCT_NAME'),
                    category=row.get('CATEGORY'),
                    min_stock_level=row.get('MIN_STOCK', 0)
                )
                self.db.add(new_item)

    def _process_sales(self, row, action):
        tid = str(row['TRANSACTION_ID'])
        existing = self.db.query(FactSales).filter(FactSales.transaction_id == tid).first()

        if action == 'DELETE':
            if existing: self.db.delete(existing)
        else:
            if existing:
                existing.quantity = row.get('QUANTITY', existing.quantity)
                existing.amount = row.get('AMOUNT', existing.amount)
            else:
                new_item = FactSales(
                    transaction_id=tid,
                    order_id=str(row.get('ORDER_ID', '')),
                    sku_id=str(row['SKU_ID']),
                    quantity=row['QUANTITY'],
                    order_date=pd.to_datetime(row['ORDER_DATE']),
                    source='EXCEL'
                )
                self.db.add(new_item)

    def _process_customer(self, row, action):
        pass # Similar logic

    def _process_vendor(self, row, action):
        pass # Similar logic
