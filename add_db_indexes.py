import os
import sqlite3

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, 'AI_Land_Registry', 'land_registry.db'),
        os.path.join(base_dir, 'land_registry.db'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return os.path.join(base_dir, 'AI_Land_Registry', 'land_registry.db')

def add_indexes():
    db_path = get_db_path()
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    indexes = [
        ("idx_lands_owner_id", "lands", "owner_id"),
        ("idx_lands_pid", "lands", "pid"),
        ("idx_lands_city", "lands", "city"),
        ("idx_lands_status", "lands", "status"),
        ("idx_documents_land_id", "documents", "land_id"),
        ("idx_documents_status", "documents", "verification_status"),
        ("idx_land_requests_land_id", "land_requests", "land_id"),
        ("idx_land_requests_seller_id", "land_requests", "seller_id"),
        ("idx_land_requests_buyer_id", "land_requests", "buyer_id"),
        ("idx_land_requests_status", "land_requests", "status"),
        ("idx_ownership_history_land_id", "ownership_history", "land_id"),
        ("idx_ownership_history_prev_owner", "ownership_history", "previous_owner_id"),
        ("idx_ownership_history_new_owner", "ownership_history", "new_owner_id"),
        ("idx_ownership_history_transfer_date", "ownership_history", "transfer_date"),
        ("idx_fraud_records_land_id", "fraud_records", "land_id"),
        ("idx_fraud_records_status", "fraud_records", "status"),
        ("idx_price_predictions_land_id", "price_predictions", "land_id"),
        ("idx_users_role", "users", "role"),
    ]

    print("\n--- Creating SQLite Database Performance Indexes ---")
    for idx_name, table, column in indexes:
        sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column});"
        cursor.execute(sql)
        print(f"  [OK] Index '{idx_name}' created on {table}({column})")

    # Set PRAGMAs for high performance
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA cache_size = -64000;")
    cursor.execute("PRAGMA temp_store = MEMORY;")

    conn.commit()

    # List all indexes to verify
    cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index';")
    all_idx = cursor.fetchall()
    print(f"\nSuccessfully verified {len(all_idx)} database indexes!")
    conn.close()

if __name__ == '__main__':
    add_indexes()
