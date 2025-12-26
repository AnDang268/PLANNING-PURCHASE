
from backend.database import SessionLocal
from backend.models import DimCustomers

def check_one():
    db = SessionLocal()
    try:
        cid = 'QUANGVINH' # Copied from log. Note: SyncService log truncated the ID?
        # Log said: Row Committed..QUANGVINH - QUANG VINH- DIỄN CHÂU
        # The ID is usually before the hyphen.
        # But wait, the log was "Row Committed..{item}"?
        # I didn't print item ID in the "Row Committed" log.
        # I printed "Row Committed."
        # The log snippet showed: "    > Row Committed..QUANGVANTOAN"
        # Ah! I didn't add a newline in the print? "print(..., flush=True)" adds newline by default.
        # But previous logs might have lacked newline?
        # "    > Row Committed." has newline.
        # The snippet "    > Row Committed..QUANGVANTOAN" implies the NEXT line started on the same line?
        # No, ".." probably means previous line ended with "ed" and next line started with "."?
        # No.
        
        # Let's search by Name roughly
        objs = db.query(DimCustomers).filter(DimCustomers.customer_name.like(u'%QUANG VINH%')).all()
        print(f"Found {len(objs)} matches for QUANG VINH:")
        for o in objs:
            print(f"{o.customer_id} - {o.customer_name}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_one()
