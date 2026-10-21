import time
import sqlite3

DB_PATH = 'AI_Land_Registry/land_registry.db'

def test_performance():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("==================================================")
    print("      PERFORMANCE BENCHMARK TEST (100k DB)        ")
    print("==================================================")

    # 1. Test Search by Survey Number
    t0 = time.perf_counter()
    c.execute("SELECT id, survey_number, pid, city, price FROM lands WHERE survey_number LIKE '%MUM-0005%' LIMIT 20;")
    res_survey = c.fetchall()
    t_survey = (time.perf_counter() - t0) * 1000
    print(f"1. Search by Survey Number: {t_survey:.2f} ms ({len(res_survey)} results)")

    # 2. Test Search by Property PID
    t0 = time.perf_counter()
    c.execute("SELECT id, survey_number, pid, city, price FROM lands WHERE pid LIKE '%PID-KA-BLR%' LIMIT 20;")
    res_pid = c.fetchall()
    t_pid = (time.perf_counter() - t0) * 1000
    print(f"2. Search by Property PID: {t_pid:.2f} ms ({len(res_pid)} results)")

    # 3. Test Search by City
    t0 = time.perf_counter()
    c.execute("SELECT id, survey_number, pid, city, price FROM lands WHERE city = 'Mumbai' LIMIT 20 OFFSET 100;")
    res_city = c.fetchall()
    t_city = (time.perf_counter() - t0) * 1000
    print(f"3. Search by City with LIMIT/OFFSET: {t_city:.2f} ms ({len(res_city)} results)")

    # 4. Test Paginated Ownership History Join
    t0 = time.perf_counter()
    c.execute("""
        SELECT h.id, h.transfer_ref, h.transfer_price, h.transfer_date, l.survey_number, u.username
        FROM ownership_history h
        JOIN lands l ON h.land_id = l.id
        JOIN users u ON h.new_owner_id = u.id
        ORDER BY h.transfer_date DESC
        LIMIT 20 OFFSET 500;
    """)
    res_join = c.fetchall()
    t_join = (time.perf_counter() - t0) * 1000
    print(f"4. Paginated Ownership History Join (OFFSET 500): {t_join:.2f} ms ({len(res_join)} results)")

    # 5. Test Analytics Aggregation (GROUP BY city)
    t0 = time.perf_counter()
    c.execute("SELECT city, COUNT(*), AVG(price) FROM lands GROUP BY city;")
    res_agg = c.fetchall()
    t_agg = (time.perf_counter() - t0) * 1000
    print(f"5. Analytics GROUP BY City Aggregation: {t_agg:.2f} ms ({len(res_agg)} groups)")

    # 6. Test Dashboard Count Statistics
    t0 = time.perf_counter()
    c.execute("SELECT COUNT(*) FROM users WHERE role='citizen';")
    cnt_cit = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM lands;")
    cnt_land = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM land_requests;")
    cnt_req = c.fetchone()[0]
    t_stats = (time.perf_counter() - t0) * 1000
    print(f"6. Dashboard Count Statistics ({cnt_cit:,} citizens, {cnt_land:,} lands, {cnt_req:,} reqs): {t_stats:.2f} ms")

    # 7. EXPLAIN QUERY PLAN for Land Search
    c.execute("EXPLAIN QUERY PLAN SELECT id FROM lands WHERE owner_id = 500 ORDER BY id DESC LIMIT 20;")
    qp = c.fetchall()
    print("\nQuery Plan for owner_id lookup:")
    for row in qp:
        print("  ", row)

    print("==================================================")
    conn.close()

if __name__ == '__main__':
    test_performance()
