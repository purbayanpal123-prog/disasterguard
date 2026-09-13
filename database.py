import sqlite3
import os
import hashlib
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "disasterguard.db")

def get_ist_time() -> str:
    ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return ist.strftime("%I:%M:%S %p IST")

def hash_password(password: str) -> str:
    salt = "DisasterGuard_Salt_2026_PurbayanPal"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table (Individual Citizens / Victims)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email_or_phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            blood_group TEXT DEFAULT 'Unknown',
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            created_at TEXT
        )
    """)
    
    # 2. SOS Records Table (Filtered per user for citizens, aggregated for Admin)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_records (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            accuracy REAL DEFAULT 10.0,
            vulnerable INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'P1 (HIGH)',
            status TEXT DEFAULT 'RECEIVED',
            assigned_unit TEXT,
            safe_shelter TEXT DEFAULT 'Guwahati Medical College & Hospital (GMCH)',
            target TEXT DEFAULT 'CONTROL_ROOM',
            timestamp TEXT,
            created_epoch INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 3. 2-Way Intercom Messages Table (Private per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            sender TEXT NOT NULL,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT,
            created_epoch INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 4. System Settings Table (SMS Gateway credentials, Fast2SMS API Key)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    
    # Seed default demonstration citizen if no user exists
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        demo_pass = hash_password("123456")
        cursor.execute("""
            INSERT INTO users (name, email_or_phone, password_hash, blood_group, emergency_contact_name, emergency_contact_phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Purbayan Pal (Citizen)",
            "+91 98300 12345",
            demo_pass,
            "O+ Positive",
            "Emergency Family Support",
            "+91 98300 99999",
            get_ist_time()
        ))
        conn.commit()
        
    conn.close()

def register_user(name: str, email_or_phone: str, password: str, blood_group: str = "Unknown",
                  emergency_name: str = "", emergency_phone: str = "") -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    now = get_ist_time()
    try:
        cursor.execute("""
            INSERT INTO users (name, email_or_phone, password_hash, blood_group, emergency_contact_name, emergency_contact_phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email_or_phone.strip(), pwd_hash, blood_group, emergency_name.strip(), emergency_phone.strip(), now))
        conn.commit()
        user_id = cursor.lastrowid
        return {
            "success": True,
            "user": {
                "id": user_id,
                "name": name,
                "email_or_phone": email_or_phone,
                "blood_group": blood_group,
                "emergency_contact_name": emergency_name,
                "emergency_contact_phone": emergency_phone,
                "created_at": now
            }
        }
    except sqlite3.IntegrityError:
        return {"success": False, "error": "This Phone Number / Email is already registered! Please login."}
    finally:
        conn.close()

def authenticate_user(email_or_phone: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    
    # 1. Exact match
    cursor.execute("""
        SELECT id, name, email_or_phone, blood_group, emergency_contact_name, emergency_contact_phone, created_at
        FROM users
        WHERE email_or_phone = ? AND password_hash = ?
    """, (email_or_phone.strip(), pwd_hash))
    row = cursor.fetchone()
    if row:
        conn.close()
        return dict(row)
        
    # 2. Normalized 10-digit phone match
    existing = get_user_by_phone(email_or_phone)
    if existing:
        cursor.execute("SELECT password_hash FROM users WHERE id = ?", (existing["id"],))
        r = cursor.fetchone()
        if r and r["password_hash"] == pwd_hash:
            conn.close()
            return existing

    conn.close()
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email_or_phone, blood_group, emergency_contact_name, emergency_contact_phone, created_at
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    p_clean = phone.strip()
    digits = re.sub(r'[^0-9]', '', p_clean)
    cursor.execute("""
        SELECT id, name, email_or_phone, blood_group, emergency_contact_name, emergency_contact_phone, created_at
        FROM users
    """)
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        stored = row["email_or_phone"].strip()
        if stored == p_clean:
            return dict(row)
        stored_digits = re.sub(r'[^0-9]', '', stored)
        if digits and stored_digits:
            if digits == stored_digits:
                return dict(row)
            d_tail = digits[-10:] if len(digits) >= 10 else digits
            s_tail = stored_digits[-10:] if len(stored_digits) >= 10 else stored_digits
            if len(d_tail) == 10 and len(s_tail) == 10 and d_tail == s_tail:
                return dict(row)
    return None

def create_or_get_otp_user(phone: str, name: str = "", blood_group: str = "Unknown",
                           emergency_name: str = "", emergency_phone: str = "") -> Dict[str, Any]:
    existing = get_user_by_phone(phone)
    if existing:
        if name and existing.get("name") != name:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET name = ?, blood_group = ?, emergency_contact_name = ?, emergency_contact_phone = ?
                WHERE id = ?
            """, (name, blood_group, emergency_name, emergency_phone, existing["id"]))
            conn.commit()
            conn.close()
            existing["name"] = name
            existing["blood_group"] = blood_group
            existing["emergency_contact_name"] = emergency_name
            existing["emergency_contact_phone"] = emergency_phone
        return existing

    display_name = name.strip() if name.strip() else f"Citizen ({phone[-4:] if len(phone)>=4 else phone})"
    res = register_user(display_name, phone, "OTP_VERIFIED", blood_group, emergency_name, emergency_phone)
    if res.get("success"):
        return res["user"]
    return get_user_by_phone(phone) or {"id": 1, "name": display_name, "email_or_phone": phone}

def save_sos(sos: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    epoch = int(datetime.utcnow().timestamp())
    cursor.execute("""
        INSERT OR REPLACE INTO sos_records 
        (id, user_id, name, phone, lat, lng, accuracy, vulnerable, priority, status, assigned_unit, safe_shelter, target, timestamp, created_epoch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sos["id"],
        sos.get("user_id"),
        sos["name"],
        sos["phone"],
        sos["lat"],
        sos["lng"],
        sos.get("accuracy", 10.0),
        1 if sos.get("vulnerable") else 0,
        sos.get("priority", "P1 (HIGH)"),
        sos.get("status", "RECEIVED"),
        sos.get("assigned_unit"),
        sos.get("safe_shelter", "Guwahati Medical College & Hospital (GMCH)"),
        sos.get("target", "CONTROL_ROOM"),
        sos.get("timestamp", get_ist_time()),
        epoch
    ))
    conn.commit()
    conn.close()
    return sos

def get_user_sos_history(user_id: int) -> List[Dict[str, Any]]:
    """Returns SOS records specifically belonging to this authenticated user only."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sos_records WHERE user_id = ? ORDER BY created_epoch DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_active_sos() -> List[Dict[str, Any]]:
    """Aggregates all active distress records for the Control Room Admin view."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sos_records ORDER BY created_epoch DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_sos_status(sos_id: str, status: str, assigned_unit: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if assigned_unit:
        cursor.execute("UPDATE sos_records SET status = ?, assigned_unit = ? WHERE id = ?", (status, assigned_unit, sos_id))
    else:
        cursor.execute("UPDATE sos_records SET status = ? WHERE id = ?", (status, sos_id))
    conn.commit()
    conn.close()

def save_chat_message(msg: Dict[str, Any]):
    conn = get_db()
    cursor = conn.cursor()
    epoch = int(datetime.utcnow().timestamp())
    cursor.execute("""
        INSERT OR REPLACE INTO chat_messages (id, user_id, sender, role, text, timestamp, created_epoch)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        msg["id"],
        msg.get("user_id"),
        msg["sender"],
        msg["role"],
        msg["text"],
        msg.get("timestamp", get_ist_time()),
        epoch
    ))
    conn.commit()
    conn.close()

def get_user_chat_history(user_id: int) -> List[Dict[str, Any]]:
    """Fetches chat messages strictly between this citizen and the Control Room."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chat_messages WHERE user_id = ? ORDER BY created_epoch ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_chat_history() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chat_messages ORDER BY created_epoch ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_setting(key: str, default: str = "") -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value.strip()))
    conn.commit()
    conn.close()
