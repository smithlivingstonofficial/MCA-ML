from sqlalchemy import text
from backend.app.db.session import engine, Base
import backend.app.db.models  # Ensure all models are registered


def run_migrations():
    print("[*] Running schema synchronizations...")
    # 1. Create any missing tables (inventory_items, inventory_lots, equipment, staff_members, stock_movements)
    Base.metadata.create_all(bind=engine)

    # 2. Check and alter roster_assignments if needed
    with engine.connect() as conn:
        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(roster_assignments)")).fetchall()]
        print(f"    - Existing roster_assignments columns: {cols}")
        if "staff_id" not in cols:
            conn.execute(text("ALTER TABLE roster_assignments ADD COLUMN staff_id VARCHAR(36)"))
            print("    [+] Added missing column 'staff_id' to roster_assignments")
        if "status" not in cols:
            conn.execute(text("ALTER TABLE roster_assignments ADD COLUMN status VARCHAR(20) DEFAULT 'Scheduled'"))
            print("    [+] Added missing column 'status' to roster_assignments")
        conn.commit()
    print("[+] Database schema up to date.")


if __name__ == "__main__":
    run_migrations()
