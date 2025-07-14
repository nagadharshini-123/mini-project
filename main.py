import cv2
import easyocr
import sqlite3
from datetime import datetime

# Database creation

def init_db():
    conn = sqlite3.connect("anpr_logs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT NOT NULL,
            access TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Load Registered Plates

def load_registered_plates(filename="registered_plates.txt"):
    try:
        with open(filename, 'r') as file:
            return set(line.strip().upper() for line in file)
    except FileNotFoundError:
        print("[WARNING] 'registered_plates.txt' not found.")
        return set()

# Log to Database

def log_access(plate, access):
    conn = sqlite3.connect("anpr_logs.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO access_logs (plate, access, timestamp) VALUES (?, ?, ?)", (plate, access, now))
    conn.commit()
    conn.close()

# Start Camera & Detect

def run_anpr():
    init_db()
    registered_plates = load_registered_plates()
    reader = easyocr.Reader(['en'], gpu=False)
    cap = cv2.VideoCapture(0)

    print("[INFO] ANPR system running... Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray)

        for (bbox, text, prob) in results:
            plate = text.replace(" ", "").upper()
            if 6 <= len(plate) <= 12:  # Basic plate check
                access = "ALLOWED" if plate in registered_plates else "DENIED"
                color = (0, 255, 0) if access == "ALLOWED" else (0, 0, 255)

                # Draw box and text
                cv2.rectangle(frame, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), color, 2)
                cv2.putText(frame, f"{plate} - {access}", tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                # Log result
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{now}] Plate: {plate} | Access: {access}")
                log_access(plate, access)
                break  # Process one plate per frame

        cv2.imshow("ANPR Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    run_anpr()
