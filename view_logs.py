import sqlite3

def show_logs():
    conn = sqlite3.connect("anpr_logs.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM access_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    
    print(f"{'ID':<5} {'Plate':<15} {'Access':<10} {'Timestamp'}")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<15} {row[2]:<10} {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    show_logs()
