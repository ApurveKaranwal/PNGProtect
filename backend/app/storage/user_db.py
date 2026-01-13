from __future__ import annotations
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

DB_PATH = Path(__file__).parent / "users.db"

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    full_name: str
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None

@dataclass
class UserSession:
    token: str
    user_id: str
    expires_at: datetime

@dataclass
class Template:
    id: str
    user_id: str
    name: str
    strength: int
    description: str
    is_default: bool
    created_at: datetime

class UserStore:
    _instance: "UserStore | None" = None

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        # Users table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'free',
                created_at TEXT NOT NULL,
                last_login TEXT
            );
        """)
        
        # Sessions table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # Templates table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS watermark_templates (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                strength INTEGER NOT NULL,
                description TEXT,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # Bulk operations table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bulk_operations (
                operation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                total_files INTEGER DEFAULT 0,
                processed_files INTEGER DEFAULT 0,
                failed_files INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        self.conn.commit()
        self._create_default_templates()

    def _create_default_templates(self):
        # Check if default templates exist
        cur = self.conn.execute("SELECT COUNT(*) FROM watermark_templates WHERE is_default = TRUE")
        if cur.fetchone()[0] == 0:
            default_templates = [
                ("default-light", "system", "Light Protection", 3, "Minimal watermark for social media"),
                ("default-medium", "system", "Medium Protection", 5, "Balanced protection for portfolios"),
                ("default-strong", "system", "Strong Protection", 8, "Maximum protection for commercial use")
            ]
            
            for template_id, user_id, name, strength, desc in default_templates:
                self.conn.execute("""
                    INSERT OR IGNORE INTO watermark_templates 
                    (id, user_id, name, strength, description, is_default, created_at)
                    VALUES (?, ?, ?, ?, ?, TRUE, ?)
                """, (template_id, user_id, name, strength, desc, datetime.utcnow().isoformat()))
            
            self.conn.commit()

    @classmethod
    def get_instance(cls) -> "UserStore":
        if cls._instance is None:
            cls._instance = UserStore()
        return cls._instance

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email: str, password: str, full_name: str, role: str = "free") -> str:
        user_id = secrets.token_urlsafe(16)
        password_hash = self.hash_password(password)
        created_at = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            INSERT INTO users (id, email, password_hash, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, email, password_hash, full_name, role, created_at))
        self.conn.commit()
        return user_id

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        password_hash = self.hash_password(password)
        cur = self.conn.execute("""
            SELECT * FROM users WHERE email = ? AND password_hash = ?
        """, (email, password_hash))
        
        row = cur.fetchone()
        if row:
            # Update last login
            self.conn.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (datetime.utcnow().isoformat(), row["id"]))
            self.conn.commit()
            
            return User(
                id=row["id"],
                email=row["email"],
                password_hash=row["password_hash"],
                full_name=row["full_name"],
                role=row["role"],
                created_at=datetime.fromisoformat(row["created_at"]),
                last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
            )
        return None

    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        self.conn.execute("""
            INSERT INTO user_sessions (token, user_id, expires_at)
            VALUES (?, ?, ?)
        """, (token, user_id, expires_at.isoformat()))
        self.conn.commit()
        return token

    def get_user_by_token(self, token: str) -> Optional[User]:
        cur = self.conn.execute("""
            SELECT u.* FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token, datetime.utcnow().isoformat()))
        
        row = cur.fetchone()
        if row:
            return User(
                id=row["id"],
                email=row["email"],
                password_hash=row["password_hash"],
                full_name=row["full_name"],
                role=row["role"],
                created_at=datetime.fromisoformat(row["created_at"]),
                last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
            )
        return None

    def get_user_templates(self, user_id: str) -> List[Template]:
        cur = self.conn.execute("""
            SELECT * FROM watermark_templates 
            WHERE user_id = ? OR is_default = TRUE
            ORDER BY is_default DESC, created_at DESC
        """, (user_id,))
        
        templates = []
        for row in cur.fetchall():
            templates.append(Template(
                id=row["id"],
                user_id=row["user_id"],
                name=row["name"],
                strength=row["strength"],
                description=row["description"],
                is_default=bool(row["is_default"]),
                created_at=datetime.fromisoformat(row["created_at"])
            ))
        return templates

    def create_template(self, user_id: str, name: str, strength: int, description: str) -> str:
        template_id = secrets.token_urlsafe(12)
        created_at = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            INSERT INTO watermark_templates (id, user_id, name, strength, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (template_id, user_id, name, strength, description, created_at))
        self.conn.commit()
        return template_id

    def get_user_stats(self, user_id: str) -> dict:
        # Import here to avoid circular imports
        from app.storage.db import WatermarkStore
        watermark_store = WatermarkStore.get_instance()
        
        # Get watermark count from the watermarks database
        try:
            cur = watermark_store.conn.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(total_bits), 0) as total_bits
                FROM watermarks WHERE owner_id = ?
            """, (user_id,))
            watermark_data = cur.fetchone()
        except Exception as e:
            print(f"Error querying watermarks: {e}")
            # If watermarks table doesn't exist, return default values
            watermark_data = {"count": 0, "total_bits": 0}
        
        # Calculate storage used (rough estimate)
        total_bits = watermark_data["total_bits"] if isinstance(watermark_data, dict) else watermark_data[1]
        storage_mb = (total_bits or 0) / 8 / 1024 / 1024
        
        # Get recent activity from watermarks database
        recent_activity = []
        try:
            cur = watermark_store.conn.execute("""
                SELECT watermark_id, image_hash as original_filename, owner_id, 
                       strength, total_bits, created_at
                FROM watermarks WHERE owner_id = ?
                ORDER BY created_at DESC LIMIT 5
            """, (user_id,))
            
            for row in cur.fetchall():
                recent_activity.append({
                    "watermark_id": row["watermark_id"],
                    "original_filename": row["original_filename"][:20] + "...",
                    "owner_id": row["owner_id"],
                    "strength": row["strength"],
                    "file_size_mb": (row["total_bits"] or 0) / 8 / 1024 / 1024,
                    "created_at": row["created_at"],
                    "verification_count": 0  # Placeholder
                })
        except Exception as e:
            print(f"Error querying recent activity: {e}")
            # If watermarks table doesn't exist, return empty activity
            recent_activity = []
        
        count = watermark_data["count"] if isinstance(watermark_data, dict) else watermark_data[0]
        
        return {
            "total_watermarks": count,
            "total_verifications": count * 2,  # Rough estimate
            "storage_used_mb": round(storage_mb, 2),
            "protection_score": min(95, 60 + (count * 2)),
            "recent_activity": recent_activity
        }