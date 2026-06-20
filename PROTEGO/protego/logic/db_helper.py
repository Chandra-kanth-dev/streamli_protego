import os
import sqlite3
from pathlib import Path
import datetime
from typing import List, Dict, Any, Tuple
from supabase import create_client, Client

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "protego" / "data"
DB_PATH = DB_DIR / "protego_local.db"

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)

SUPABASE_URL = "https://wyaokrorqdnbcwkgjcho.supabase.co"
SUPABASE_KEY = "sb_publishable_rdlUtCFXg5bMKQEmHuEPRw_5JBvWXQf"

_supabase_client = None

def get_supabase() -> Client:
    """Initialize and return Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception:
            _supabase_client = None
    return _supabase_client

# ---------------------------------------------------------
# SQLite Database Setup & Mock Data Seeding
# ---------------------------------------------------------
def init_local_db():
    """Create local SQLite database and populate it with rich mock data if empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        password TEXT,
        role TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        message TEXT,
        response TEXT,
        risk TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        latitude REAL,
        longitude REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS safety_plans (
        user_id TEXT PRIMARY KEY,
        safe_contacts TEXT,
        warning_signs TEXT,
        safe_places TEXT,
        escape_steps TEXT,
        pack_list TEXT,
        code_word TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Check if empty, and seed if so
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        print("Seeding mock database...")
        # 1. Seed Users
        mock_users = [
            ("u1", "Sarah Jenkins", "sarah@example.com", "pass123", "user", "2026-06-15 08:30:00"),
            ("u2", "Priya Sharma", "priya.sharma@example.com", "pass123", "user", "2026-06-16 10:15:00"),
            ("u3", "Elena Rostova", "elena@example.com", "pass123", "user", "2026-06-17 12:00:00"),
            ("u4", "Yuki Tanaka", "yuki@example.com", "pass123", "user", "2026-06-18 09:45:00"),
            ("u5", "Amina Bello", "amina@example.com", "pass123", "user", "2026-06-18 14:20:00"),
            ("u6", "Carlos Gomez", "carlos@example.com", "pass123", "user", "2026-06-19 16:10:00"),
            ("u7", "Emily Smith", "emily@example.com", "pass123", "user", "2026-06-19 17:55:00"),
            ("admin1", "Command Center Admin", "admin@protego.org", "admin123", "admin", "2026-06-01 00:00:00")
        ]
        cursor.executemany("INSERT INTO users (id, name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?, ?)", mock_users)
        
        # 2. Seed Locations
        mock_locs = [
            ("u1", 40.7128, -74.0060, "2026-06-15 08:35:00"),  # New York
            ("u2", 19.0760, 72.8777, "2026-06-16 10:20:00"),   # Mumbai
            ("u3", 52.5200, 13.4050, "2026-06-17 12:05:00"),   # Berlin
            ("u4", 35.6762, 139.6503, "2026-06-18 09:50:00"),  # Tokyo
            ("u5", -26.2041, 28.0473, "2026-06-18 14:25:00"),  # Johannesburg
            ("u6", -23.5505, -46.6333, "2026-06-19 16:15:00"), # Sao Paulo
            ("u7", 51.5074, -0.1278, "2026-06-19 18:00:00")    # London
        ]
        cursor.executemany("INSERT INTO locations (user_id, latitude, longitude, created_at) VALUES (?, ?, ?, ?)", mock_locs)
        
        # 3. Seed Chat logs with varying risk levels
        mock_chats = [
            # Sarah Jenkins (u1)
            ("u1", "I am feeling lonely and stressed today.", "I’m really glad you reached out 🤍 I’m here with you, and I’m listening. Tell me what’s going on.", "low", "2026-06-15 08:31:00"),
            ("u1", "My husband is checking my phone and won't let me see my friends.", "That sounds like coercive control. I'm really sorry you're feeling this way 🤍 What you're experiencing is isolating, and it's a form of abuse. You deserve freedom and respect.", "medium", "2026-06-15 08:33:00"),
            ("u1", "He got angry just now and pushed me against the wall.", "I am really concerned about you 🤍 What you're describing is physical abuse, and your safety is at risk. Please make sure you are in a safe place, or contact a trusted person.", "high", "2026-06-15 08:34:00"),
            ("u1", "He has a weapon and is locking me inside the room. Call the police!", "🚨 EMERGENCY DETECTED 🚨 I care about your safety. If you can, dial 911 immediately or escape to a neighbor or public place. Do not wait!", "emergency", "2026-06-15 08:35:00"),
            
            # Priya Sharma (u2)
            ("u2", "Hello. I need someone to talk to about my relationship.", "I’m here with you, and I’m listening. Thank you for telling me how you’re feeling. What's on your mind? 🤍", "low", "2026-06-16 10:16:00"),
            ("u2", "He yells at me every single day. I feel so small.", "I’m really sorry you’re feeling this way 🤍 Constant yelling and insults can be emotionally heavy. Your feelings matter, and you deserve a supportive environment.", "medium", "2026-06-16 10:18:00"),
            ("u2", "He threatened to beat me if I try to leave the house.", "I’m really concerned about you 🤍 Threats of violence are dangerous. Please reach out to local domestic violence hotlines like 181. Your safety is paramount.", "high", "2026-06-16 10:20:00"),
            
            # Elena Rostova (u3)
            ("u3", "Hi Protego, can you help me build a safety plan?", "I’m really glad you reached out 🤍 I can definitely help you design a safety plan. What exits are near you, and who is a trusted neighbor you can contact?", "low", "2026-06-17 12:01:00"),
            
            # Yuki Tanaka (u4)
            ("u4", "I'm having a panic attack because he's banging on the door.", "I'm worried about what you're going through. What you are describing sounds serious. Try to breathe slowly, find a lockable room if possible, and reach out to local police (110) or counseling (0120-279-338) immediately. 🤍", "high", "2026-06-18 09:48:00"),
            
            # Amina Bello (u5)
            ("u5", "I feel unsafe in my house.", "What you’re describing sounds serious, and I care about your safety. Let's work together on a safe way to get to shelter or contact local aid. 🤍", "high", "2026-06-18 14:22:00"),
            
            # Carlos Gomez (u6)
            ("u6", "He checks my location constantly.", "I'm sorry you're dealing with this. This is monitoring behavior and a form of digital control. Make sure your location sharing is turned off if safe to do so. 🤍", "medium", "2026-06-19 16:12:00")
        ]
        cursor.executemany("INSERT INTO chats (user_id, message, response, risk, created_at) VALUES (?, ?, ?, ?, ?)", mock_chats)
        
        conn.commit()
    conn.close()

# Initialize DB on load
init_local_db()

# ---------------------------------------------------------
# Unified Data Access Functions (Supabase with SQLite Fallback)
# ---------------------------------------------------------
def get_users() -> List[Dict[str, Any]]:
    """Fetch all users."""
    supabase = get_supabase()
    if supabase:
        try:
            res = supabase.table("users").select("*").execute()
            return res.data
        except Exception as e:
            print(f"Supabase error fetching users: {e}. Falling back to SQLite.")
            
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_chats() -> List[Dict[str, Any]]:
    """Fetch all chats."""
    supabase = get_supabase()
    if supabase:
        try:
            res = supabase.table("chats").select("*").execute()
            return res.data
        except Exception as e:
            print(f"Supabase error fetching chats: {e}. Falling back to SQLite.")
            
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_locations() -> List[Dict[str, Any]]:
    """Fetch all locations."""
    supabase = get_supabase()
    if supabase:
        try:
            res = supabase.table("locations").select("*").execute()
            return res.data
        except Exception as e:
            print(f"Supabase error fetching locations: {e}. Falling back to SQLite.")
            
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_chat(user_id: str, message: str, response: str, risk: str) -> bool:
    """Save a chat record to the database."""
    supabase = get_supabase()
    saved_online = False
    
    if supabase:
        try:
            res = supabase.table("chats").insert([{
                "user_id": user_id,
                "message": message,
                "response": response,
                "risk": risk
            }]).execute()
            saved_online = True
        except Exception as e:
            print(f"Supabase error saving chat: {e}. Saving to SQLite only.")
            
    # Always write to SQLite locally to keep local sync intact
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats (user_id, message, response, risk) VALUES (?, ?, ?, ?)",
            (user_id, message, response, risk)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"SQLite save error: {e}")
        return False

def save_location(user_id: str, latitude: float, longitude: float) -> bool:
    """Save a location pin for an emergency/user coordinate."""
    supabase = get_supabase()
    saved_online = False
    
    if supabase:
        try:
            res = supabase.table("locations").insert([{
                "user_id": user_id,
                "latitude": latitude,
                "longitude": longitude
            }]).execute()
            saved_online = True
        except Exception as e:
            print(f"Supabase error saving location: {e}. Saving to SQLite only.")
            
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO locations (user_id, latitude, longitude) VALUES (?, ?, ?)",
            (user_id, latitude, longitude)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"SQLite location save error: {e}")
        return False

def add_user(user_id: str, name: str, email: str, role: str = "user") -> bool:
    """Add a new user."""
    supabase = get_supabase()
    
    if supabase:
        try:
            res = supabase.table("users").insert([{
                "id": user_id,
                "name": name,
                "email": email,
                "role": role
            }]).execute()
        except Exception as e:
            print(f"Supabase error adding user: {e}")
            
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, role) VALUES (?, ?, ?, ?)",
            (user_id, name, email, role)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"SQLite user save error: {e}")
        return False

def save_safety_plan(user_id: str, safe_contacts: str, warning_signs: str, safe_places: str, escape_steps: str, pack_list: str, code_word: str) -> bool:
    """Save/Update a user's safety plan."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO safety_plans 
            (user_id, safe_contacts, warning_signs, safe_places, escape_steps, pack_list, code_word) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, safe_contacts, warning_signs, safe_places, escape_steps, pack_list, code_word)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"SQLite safety plan save error: {e}")
        return False

def get_safety_plan(user_id: str) -> Dict[str, str]:
    """Retrieve a user's safety plan from SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM safety_plans WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception as e:
        print(f"SQLite safety plan retrieve error: {e}")
    return {}
