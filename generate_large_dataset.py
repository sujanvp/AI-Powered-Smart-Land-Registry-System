import os
import sys
import sqlite3
import random
import json
import hashlib
from datetime import datetime, timedelta

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, 'AI_Land_Registry', 'land_registry.db'),
        os.path.join(base_dir, 'land_registry.db'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Default fallback
    return os.path.join(base_dir, 'AI_Land_Registry', 'land_registry.db')

DB_PATH = get_db_path()

CITIES_DATA = [
    {"city": "Mumbai", "state": "Maharashtra", "code": "MUM", "scode": "MH", "lat": 19.0760, "lng": 72.8777, "rate": 12000,
     "localities": ["Bandra West", "Andheri East", "Juhu", "Powai", "Worli", "Borivali West", "Thane West", "Navi Mumbai"]},
    {"city": "Pune", "state": "Maharashtra", "code": "PUN", "scode": "MH", "lat": 18.5204, "lng": 73.8567, "rate": 6500,
     "localities": ["Kothrud", "Baner", "Viman Nagar", "Wakad", "Hinjawadi", "Hadapsar", "Aundh"]},
    {"city": "Bengaluru", "state": "Karnataka", "code": "BLR", "scode": "KA", "lat": 12.9716, "lng": 77.5946, "rate": 8500,
     "localities": ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar", "Electronic City", "Yelahanka"]},
    {"city": "Hyderabad", "state": "Telangana", "code": "HYD", "scode": "TG", "lat": 17.3850, "lng": 78.4867, "rate": 7000,
     "localities": ["Gachibowli", "HITEC City", "Jubilee Hills", "Banjara Hills", "Kondapur", "Madhapur", "Kukatpally"]},
    {"city": "Delhi", "state": "Delhi", "code": "DLH", "scode": "DL", "lat": 28.6139, "lng": 77.2090, "rate": 11000,
     "localities": ["Vasant Kunj", "Dwarka", "Rohini", "Saket", "Greater Kailash", "Janakpuri", "Lajpat Nagar"]},
    {"city": "Noida", "state": "Uttar Pradesh", "code": "NDA", "scode": "UP", "lat": 28.5355, "lng": 77.3910, "rate": 5500,
     "localities": ["Sector 62", "Sector 150", "Sector 18", "Sector 137", "Sector 50"]},
    {"city": "Ahmedabad", "state": "Gujarat", "code": "AMD", "scode": "GJ", "lat": 23.0225, "lng": 72.5714, "rate": 4500,
     "localities": ["Bodakdev", "Satellite", "SG Highway", "Prahlad Nagar", "Vastrapur"]},
    {"city": "Chennai", "state": "Tamil Nadu", "code": "CHE", "scode": "TN", "lat": 13.0827, "lng": 80.2707, "rate": 7500,
     "localities": ["Velachery", "Adyar", "Anna Nagar", "T. Nagar", "OMR", "Porur"]},
    {"city": "Kolkata", "state": "West Bengal", "code": "KOL", "scode": "WB", "lat": 22.5726, "lng": 88.3639, "rate": 5000,
     "localities": ["Salt Lake", "New Town", "Ballygunge", "Rajarhat", "Alipore"]},
    {"city": "Jaipur", "state": "Rajasthan", "code": "JPR", "scode": "RJ", "lat": 26.9124, "lng": 75.7873, "rate": 4000,
     "localities": ["Vaishali Nagar", "Malviya Nagar", "Mansarovar", "C-Scheme", "Raja Park"]},
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Priya", "Ananya", "Vikram", "Neha", "Rahul", "Sanya", "Amit",
    "Kavya", "Suresh", "Meera", "Deepak", "Pooja", "Rajesh", "Sunita", "Arjun", "Divya", "Sanjay",
    "Ankita", "Vijay", "Shweta", "Ramesh", "Nisha", "Manish", "Preeti", "Karan", "Simran", "Alok",
    "Richa", "Gaurav", "Vandana", "Abhishek", "Sneha", "Pradeep", "Aarti", "Harish", "Ritu", "Vivek",
    "Tarun", "Bhavna", "Kunal", "Swati", "Nikhil", "Poonam", "Ashok", "Kiran", "Dinesh", "Rashmi"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Joshi", "Rao", "Nair", "Reddy",
    "Deshmukh", "Kulkarni", "Mehta", "Shah", "Chawla", "Agarwal", "Bhat", "Iyer", "Banerjee", "Chatterjee",
    "Dutta", "Das", "Yadav", "Pandey", "Tiwari", "Mishra", "Choudhury", "Saxena", "Kapoor", "Malhotra"
]

DEFAULT_PASSWORD_HASH = "scrypt:32768:8:1$0UMioZPYhtCDmHtp$6b3c90e8e0640bdc333fb8f47cdabc693810dc3120a13b3eb14bdb2bf4e7fc0daef926bedf1f966e7c440c11c9f980c69403a7140bda45c88c8e2334cc1b926f"

def random_date(start_year=2024, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 8, 30)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return (start + timedelta(seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")

def generate_dataset():
    print(f"Connecting to database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file does not exist at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys check in SQLite session
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("\n--- Initializing Pre-checks & Base Data Offsets ---")
    
    # Check current counts
    tables = ['users', 'lands', 'documents', 'land_requests', 'ownership_history', 'fraud_records', 'price_predictions']
    initial_counts = {}
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        initial_counts[tbl] = cursor.fetchone()[0]
        print(f"Current count in '{tbl}': {initial_counts[tbl]} records")

    # Get max user id offset
    cursor.execute("SELECT MAX(id) FROM users")
    max_user_id = cursor.fetchone()[0] or 0

    # Get existing citizen_ids, usernames, emails for deduplication set
    cursor.execute("SELECT citizen_id, username, email FROM users")
    existing_users = cursor.fetchall()
    existing_citizen_ids = {u[0] for u in existing_users if u[0]}
    existing_usernames = {u[1] for u in existing_users if u[1]}
    existing_emails = {u[2] for u in existing_users if u[2]}

    # 1. GENERATE USERS (~10,000 records)
    print("\n[1/7] Generating ~10,000 USERS records...")
    NUM_USERS = 10000
    user_rows = []
    
    # Roles breakdown: ~9,800 citizen, ~150 registrar, ~50 admin
    roles_pool = ['citizen'] * 9800 + ['registrar'] * 150 + ['admin'] * 50
    random.shuffle(roles_pool)

    u_offset = max_user_id + 1
    generated_user_ids = []

    for i in range(NUM_USERS):
        curr_id = u_offset + i
        role = roles_pool[i]
        
        # Unique citizen ID
        c_id = f"CTZ-2026-{curr_id:06d}"
        while c_id in existing_citizen_ids:
            curr_id += 100000
            c_id = f"CTZ-2026-{curr_id:06d}"
        existing_citizen_ids.add(c_id)

        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        uname = f"{fn} {ln}"
        if uname in existing_usernames:
            mn = random.choice(["Kumar", "Chandra", "Dev", "Mohan", "Rani", "Shree", "Singh", "Babu", "Rao", "Prasad"])
            uname = f"{fn} {mn} {ln}"
        existing_usernames.add(uname)
        email = f"{fn.lower()}.{ln.lower()}{curr_id}@registry.gov.in"

        city_info = random.choice(CITIES_DATA)
        city = city_info['city']
        state = city_info['state']
        age = random.randint(21, 75)

        # Unique Aadhar (12 digits) & PAN (10 chars)
        aadhar = f"8{curr_id:011d}"
        pan = f"P{chr(65 + (curr_id % 26))}D{curr_id % 10000:04d}{chr(65 + ((curr_id + 7) % 26))}"

        is_verified = 1 if role in ['registrar', 'admin'] or random.random() < 0.95 else 0
        created_at = random_date(2024, 2026)

        user_rows.append((
            c_id, uname, email, DEFAULT_PASSWORD_HASH, role, age, city, state, aadhar, pan, is_verified, created_at
        ))

    cursor.executemany("""
        INSERT INTO users (citizen_id, username, email, password_hash, role, age, city, state, aadhar, pan, is_verified, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, user_rows)
    conn.commit()

    # Retrieve all citizen user IDs (existing + new) for land ownership linking
    cursor.execute("SELECT id, citizen_id FROM users WHERE role = 'citizen'")
    citizen_users = cursor.fetchall()
    citizen_user_ids = [u[0] for u in citizen_users]
    citizen_id_map = {u[0]: u[1] for u in citizen_users}
    print(f"Users inserted successfully! Total citizen user pool size: {len(citizen_user_ids)}")

    # 2. GENERATE LANDS (~30,000 records)
    print("\n[2/7] Generating ~30,000 LANDS records...")
    cursor.execute("SELECT MAX(id) FROM lands")
    max_land_id = cursor.fetchone()[0] or 0

    cursor.execute("SELECT survey_number, pid FROM lands")
    existing_lands = cursor.fetchall()
    existing_surveys = {l[0] for l in existing_lands if l[0]}
    existing_pids = {l[1] for l in existing_lands if l[1]}

    NUM_LANDS = 30000
    land_rows = []
    statuses = ['verified'] * 21000 + ['pending'] * 4500 + ['for_sale'] * 3000 + ['flagged'] * 1500
    random.shuffle(statuses)

    l_offset = max_land_id + 1

    for i in range(NUM_LANDS):
        curr_l_id = l_offset + i
        city_info = random.choice(CITIES_DATA)
        locality = random.choice(city_info['localities'])
        city = city_info['city']
        state = city_info['state']
        scode = city_info['scode']
        ccode = city_info['code']

        survey_num = f"SY-{ccode}-{curr_l_id:06d}"
        pid = f"PID-{scode}-{ccode}-2026-{curr_l_id:06d}"

        owner_id = random.choice(citizen_user_ids)
        area = round(random.uniform(600.0, 25000.0), 2)
        
        # Price calculated based on city rate per sq ft + location modifier
        base_rate = city_info['rate'] * random.uniform(0.85, 1.25)
        price = round(area * base_rate, 2)

        lat = round(city_info['lat'] + random.uniform(-0.08, 0.08), 6)
        lng = round(city_info['lng'] + random.uniform(-0.08, 0.08), 6)
        status = statuses[i]
        location = f"{locality}, {city}, {state}"
        desc = f"Prime residential/commercial plot in {locality}, {city}. Clear title and road connectivity."
        
        created_at = random_date(2024, 2026)

        land_rows.append((
            survey_num, owner_id, area, location, lat, lng, status, price, desc, pid, city, state, None, None, created_at
        ))

    # Batch insert lands
    batch_size = 5000
    for b in range(0, len(land_rows), batch_size):
        chunk = land_rows[b:b + batch_size]
        cursor.executemany("""
            INSERT INTO lands (survey_number, owner_id, area, location, latitude, longitude, status, price, description, pid, city, state, image_path, aadhar_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, chunk)
        conn.commit()
        print(f"   Inserted lands batch {b + len(chunk)}/{NUM_LANDS}")

    # Fetch all valid land IDs and owners map
    cursor.execute("SELECT id, owner_id, price, area, city FROM lands")
    all_lands = cursor.fetchall()
    all_land_ids = [l[0] for l in all_lands]
    land_info_map = {l[0]: {'owner_id': l[1], 'price': l[2], 'area': l[3], 'city': l[4]} for l in all_lands}
    print(f"Lands inserted successfully! Total land pool size: {len(all_land_ids)}")

    # 3. GENERATE DOCUMENTS (~15,000 records)
    print("\n[3/7] Generating ~15,000 DOCUMENTS records...")
    NUM_DOCS = 15000
    doc_types = ['title_deed', 'tax_receipt', 'survey_map', 'transfer_deed']
    doc_statuses = ['approved'] * 12000 + ['pending'] * 1800 + ['rejected'] * 1200
    random.shuffle(doc_statuses)

    doc_rows = []
    for i in range(NUM_DOCS):
        land_id = random.choice(all_land_ids)
        doc_type = random.choice(doc_types)
        v_status = doc_statuses[i]
        file_path = f"static/uploads/doc_{land_id}_{i+1}_{doc_type}.pdf"
        hash_val = hashlib.sha256(f"doc_{land_id}_{i+1}_{file_path}".encode('utf-8')).hexdigest()
        
        if v_status == 'approved':
            notes = "OCR Verification Success: Document scan processed and matched with registry database records."
        elif v_status == 'pending':
            notes = "Document submitted for automated OCR verification and registrar audit."
        else:
            notes = "OCR Verification Discrepancy: Property survey boundary mismatch detected during automated scan."

        uploaded_at = random_date(2024, 2026)
        doc_rows.append((land_id, doc_type, file_path, hash_val, v_status, notes, uploaded_at))

    for b in range(0, len(doc_rows), batch_size):
        chunk = doc_rows[b:b + batch_size]
        cursor.executemany("""
            INSERT INTO documents (land_id, document_type, file_path, hash_value, verification_status, verification_notes, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, chunk)
        conn.commit()
        print(f"   Inserted documents batch {b + len(chunk)}/{NUM_DOCS}")

    # 4. GENERATE LAND REQUESTS (~10,000 records)
    print("\n[4/7] Generating ~10,000 LAND REQUESTS records...")
    NUM_REQUESTS = 10000
    req_statuses = ['pending'] * 4000 + ['approved'] * 4000 + ['under_review'] * 1000 + ['rejected'] * 1000
    random.shuffle(req_statuses)
    reasons = ['Sale', 'Inheritance', 'Gift']

    req_rows = []
    for i in range(NUM_REQUESTS):
        land_id = random.choice(all_land_ids)
        seller_id = land_info_map[land_id]['owner_id']
        
        # Pick buyer different from seller
        buyer_id = random.choice(citizen_user_ids)
        while buyer_id == seller_id:
            buyer_id = random.choice(citizen_user_ids)

        seller_citizen_id = citizen_id_map.get(seller_id, f"CTZ-2026-{seller_id:06d}")
        buyer_citizen_id = citizen_id_map.get(buyer_id, f"CTZ-2026-{buyer_id:06d}")

        base_price = land_info_map[land_id]['price']
        bid_price = round(base_price * random.uniform(0.90, 1.12), 2)
        transfer_reason = random.choice(reasons)
        transfer_doc = f"static/uploads/request_deed_{land_id}_{i+1}.pdf"
        status = req_statuses[i]

        rejection_reason = None
        if status == 'rejected':
            rejection_reason = random.choice([
                "Incomplete seller verification documents.",
                "Discrepancy in property valuation bid price.",
                "Encumbrance check flagged existing dispute on parcel."
            ])

        created_at = random_date(2024, 2026)
        req_rows.append((
            land_id, seller_id, buyer_id, seller_citizen_id, buyer_citizen_id,
            bid_price, transfer_reason, transfer_doc, status, rejection_reason, created_at
        ))

    for b in range(0, len(req_rows), batch_size):
        chunk = req_rows[b:b + batch_size]
        cursor.executemany("""
            INSERT INTO land_requests (land_id, seller_id, buyer_id, seller_citizen_id, buyer_citizen_id, bid_price, transfer_reason, transfer_doc_path, status, rejection_reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, chunk)
        conn.commit()
        print(f"   Inserted land_requests batch {b + len(chunk)}/{NUM_REQUESTS}")

    # 5. GENERATE OWNERSHIP HISTORY (~20,000 records)
    print("\n[5/7] Generating ~20,000 OWNERSHIP HISTORY records...")
    cursor.execute("SELECT MAX(id) FROM ownership_history")
    max_own_id = cursor.fetchone()[0] or 0

    NUM_HISTORY = 20000
    own_rows = []
    own_offset = max_own_id + 1

    for i in range(NUM_HISTORY):
        curr_ref_id = own_offset + i
        land_id = random.choice(all_land_ids)
        new_owner_id = random.choice(citizen_user_ids)

        # 30% initial registration (previous owner NULL), 70% transfer
        if random.random() < 0.30:
            previous_owner_id = None
            t_ref = f"REG-2026-{curr_ref_id:06d}"
        else:
            previous_owner_id = land_info_map[land_id]['owner_id']
            while previous_owner_id == new_owner_id:
                new_owner_id = random.choice(citizen_user_ids)
            t_ref = f"TRF-2026-{curr_ref_id:06d}"

        t_price = round(land_info_map[land_id]['price'] * random.uniform(0.88, 1.15), 2)
        t_date = random_date(2023, 2026)

        own_rows.append((land_id, previous_owner_id, new_owner_id, t_date, t_price, t_ref))

    for b in range(0, len(own_rows), batch_size):
        chunk = own_rows[b:b + batch_size]
        cursor.executemany("""
            INSERT INTO ownership_history (land_id, previous_owner_id, new_owner_id, transfer_date, transfer_price, transfer_ref)
            VALUES (?, ?, ?, ?, ?, ?)
        """, chunk)
        conn.commit()
        print(f"   Inserted ownership_history batch {b + len(chunk)}/{NUM_HISTORY}")

    # 6. GENERATE FRAUD RECORDS (~5,000 records)
    print("\n[6/7] Generating ~5,000 FRAUD RECORDS records...")
    NUM_FRAUD = 5000
    fraud_flags_pool = [
        ["Duplicate Registration"],
        ["Suspicious Ownership Change"],
        ["Duplicate Identity"],
        ["Document Mismatch"],
        ["Price Anomaly"],
        ["Duplicate Registration", "Document Mismatch"],
        ["Price Anomaly", "Suspicious Ownership Change"]
    ]

    fraud_rows = []
    for i in range(NUM_FRAUD):
        land_id = random.choice(all_land_ids)
        is_high_risk = random.random() < 0.35

        if is_high_risk:
            risk_score = round(random.uniform(0.70, 0.99), 2)
            flags = random.choice(fraud_flags_pool)
            status = random.choice(['investigating', 'confirmed_fraud'])
            feedback = f"AI Fraud Detection Flag: Risk factor(s): {', '.join(flags)} detected."
        else:
            risk_score = round(random.uniform(0.01, 0.25), 2)
            flags = []
            status = 'resolved_clear'
            feedback = "AI Fraud Scan Clear: Ownership sequence and document hash verification passed with zero anomalies."

        flags_json = json.dumps(flags)
        reported_at = random_date(2024, 2026)

        fraud_rows.append((land_id, risk_score, flags_json, status, feedback, reported_at))

    for b in range(0, len(fraud_rows), batch_size):
        chunk = fraud_rows[b:b + batch_size]
        cursor.executemany("""
            INSERT INTO fraud_records (land_id, risk_score, _fraud_flags, status, ai_feedback, reported_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, chunk)
        conn.commit()
        print(f"   Inserted fraud_records batch {b + len(chunk)}/{NUM_FRAUD}")

    # 7. GENERATE PRICE PREDICTIONS (~10,000 records)
    print("\n[7/7] Generating ~10,000 PRICE PREDICTIONS records...")
    NUM_PRED = 10000
    pred_rows = []

    for i in range(NUM_PRED):
        land_id = random.choice(all_land_ids)
        actual_price = land_info_map[land_id]['price']
        
        # Predicted price within 5% of actual price
        predicted_price = round(actual_price * random.uniform(0.95, 1.05), 2)
        low_est = round(predicted_price * 0.94, 2)
        high_est = round(predicted_price * 1.06, 2)
        confidence = round(random.uniform(0.88, 0.99), 4)
        p_date = random_date(2024, 2026)

        pred_rows.append((land_id, predicted_price, low_est, high_est, confidence, p_date))

    for b in range(0, len(pred_rows), batch_size):
        chunk = pred_rows[b:b + batch_size]
        cursor.executemany("""
            INSERT INTO price_predictions (land_id, predicted_price, low_estimate, high_estimate, confidence_score, prediction_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, chunk)
        conn.commit()
        print(f"   Inserted price_predictions batch {b + len(chunk)}/{NUM_PRED}")

    print("\n==================================================")
    print("        DATA GENERATION SUMMARY & VERIFICATION    ")
    print("==================================================")

    final_counts = {}
    total_records = 0
    print(f"{'Table Name':<22} | {'Initial':<10} | {'New Added':<10} | {'Final Count':<12}")
    print("-" * 62)
    for tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        final_counts[tbl] = cursor.fetchone()[0]
        added = final_counts[tbl] - initial_counts[tbl]
        total_records += final_counts[tbl]
        print(f"{tbl:<22} | {initial_counts[tbl]:<10} | {added:<10} | {final_counts[tbl]:<12}")

    print("-" * 62)
    print(f"TOTAL RECORDS ACROSS ALL TABLES: {total_records:,}")
    print("==================================================\n")

    conn.close()
    print("Database population completed successfully!")

if __name__ == '__main__':
    generate_dataset()
