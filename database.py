import sqlite3
import os
from typing import List, Tuple, Optional, Dict
from auth import generate_salt, hash_password, verify_password

DB_NAME = "password_manager.db"

class DatabaseManager:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables if they do not exist."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Master password storage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    master_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Saved credentials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Other',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # --- Master Password Operations ---

    def has_master_password(self) -> bool:
        """Checks if master password has already been set up."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM master_auth")
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()

    def set_master_password(self, password: str) -> bool:
        """Sets or updates the master password."""
        salt = generate_salt()
        pwd_hash = hash_password(password, salt)
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM master_auth")
            cursor.execute(
                "INSERT INTO master_auth (master_hash, salt) VALUES (?, ?)",
                (pwd_hash, salt)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def verify_master_password(self, password: str) -> bool:
        """Verifies the master password."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT master_hash, salt FROM master_auth LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return False
            return verify_password(password, row["master_hash"], row["salt"])
        finally:
            conn.close()

    # --- Credential Operations (CRUD) ---

    def check_duplicate(self, website: str, username: str, exclude_id: Optional[int] = None) -> bool:
        """Checks if a credential entry with identical website and username exists."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            website_clean = website.strip().lower()
            username_clean = username.strip().lower()

            if exclude_id is not None:
                cursor.execute("""
                    SELECT COUNT(*) FROM credentials 
                    WHERE LOWER(website) = ? AND LOWER(username) = ? AND id != ?
                """, (website_clean, username_clean, exclude_id))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM credentials 
                    WHERE LOWER(website) = ? AND LOWER(username) = ?
                """, (website_clean, username_clean))

            return cursor.fetchone()[0] > 0
        finally:
            conn.close()

    def add_credential(self, website: str, username: str, password: str, category: str = "Other", notes: str = "") -> tuple[bool, str]:
        """Adds a new credential entry. Checks for required fields and duplicate entry."""
        website = website.strip()
        username = username.strip()
        password = password.strip()
        notes = notes.strip()

        if not website or not username or not password:
            return False, "Website, Username, and Password are required fields!"

        if self.check_duplicate(website, username):
            return False, f"A credential for '{website}' with username '{username}' already exists!"

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credentials (website, username, password, category, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (website, username, password, category, notes))
            conn.commit()
            return True, "Credential added successfully!"
        finally:
            conn.close()

    def get_all_credentials(self) -> List[Dict]:
        """Fetches all credentials ordered by website name."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM credentials ORDER BY website ASC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_credential_by_id(self, cred_id: int) -> Optional[Dict]:
        """Fetches a single credential by ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM credentials WHERE id = ?", (cred_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def search_credentials(self, query: str = "", category_filter: str = "All") -> List[Dict]:
        """Searches credentials by website or username, with optional category filter."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM credentials WHERE 1=1"
            params = []

            if query:
                q = f"%{query.strip()}%"
                sql += " AND (website LIKE ? OR username LIKE ?)"
                params.extend([q, q])

            if category_filter and category_filter != "All":
                sql += " AND category = ?"
                params.append(category_filter)

            sql += " ORDER BY website ASC"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def update_credential(self, cred_id: int, website: str, username: str, password: str, category: str = "Other", notes: str = "") -> tuple[bool, str]:
        """Updates an existing credential entry."""
        website = website.strip()
        username = username.strip()
        password = password.strip()
        notes = notes.strip()

        if not website or not username or not password:
            return False, "Website, Username, and Password cannot be empty!"

        if self.check_duplicate(website, username, exclude_id=cred_id):
            return False, f"Another entry for '{website}' with username '{username}' already exists!"

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE credentials 
                SET website = ?, username = ?, password = ?, category = ?, notes = ?
                WHERE id = ?
            """, (website, username, password, category, notes, cred_id))
            conn.commit()
            return True, "Credential updated successfully!"
        finally:
            conn.close()

    def delete_credential(self, cred_id: int) -> bool:
        """Deletes a credential by ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM credentials WHERE id = ?", (cred_id,))
            conn.commit()
            return True
        finally:
            conn.close()
