import sqlite3
import threading
import random
from datetime import datetime, timedelta
from config import DATABASE_PATH, DEFAULT_WAIFU_LIMIT, DEFAULT_GROUP_MODE

class Database:
    def __init__(self):
        self.lock = threading.Lock()
        self.init_database()
    
    def get_connection(self):
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Groups table - stores group settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    mode TEXT CHECK(mode IN ('waifu', 'husbando')) DEFAULT 'waifu',
                    waifu_limit INTEGER DEFAULT 10,
                    message_count INTEGER DEFAULT 0,
                    last_drop TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Characters table - OuraDB format
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    series_name TEXT NOT NULL,
                    image_url TEXT,
                    gender TEXT CHECK(gender IN ('waifu', 'husbando')) NOT NULL,
                    added_by INTEGER,
                    rarity TEXT DEFAULT 'Common',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User collections - claimed characters with counts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    character_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    count INTEGER DEFAULT 1,
                    first_claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters (id),
                    UNIQUE(user_id, character_id)
                )
            ''')
            
            # Trading table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER NOT NULL,
                    character_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    status TEXT CHECK(status IN ('pending', 'accepted', 'rejected', 'cancelled')) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters (id)
                )
            ''')
            
            # Character drops (active drops waiting to be caught)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS active_drops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    character_id INTEGER NOT NULL,
                    message_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters (id)
                )
            ''')
            
            # Special users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS special_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Banned users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS banned_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    reason TEXT,
                    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
    
    # GROUP MANAGEMENT
    def register_group(self, group_id, mode=None):
        """Register a new group or update existing group"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO groups (group_id, mode, waifu_limit, message_count, created_at)
                VALUES (?, ?, ?, 
                    COALESCE((SELECT message_count FROM groups WHERE group_id = ?), 0),
                    COALESCE((SELECT created_at FROM groups WHERE group_id = ?), CURRENT_TIMESTAMP))
            ''', (group_id, mode or DEFAULT_GROUP_MODE, DEFAULT_WAIFU_LIMIT, group_id, group_id))
            
            conn.commit()
            conn.close()
    
    def get_group(self, group_id):
        """Get group information"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
            group = cursor.fetchone()
            
            conn.close()
            return dict(group) if group else None
    
    def set_group_mode(self, group_id, mode):
        """Set group mode (waifu/husbando)"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE groups SET mode = ? WHERE group_id = ?", (mode, group_id))
            conn.commit()
            conn.close()
    
    def set_waifu_limit(self, group_id, limit):
        """Set waifu limit for group"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE groups SET waifu_limit = ? WHERE group_id = ?", (limit, group_id))
            conn.commit()
            conn.close()
    
    def increment_message_count(self, group_id):
        """Increment message count for group"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE groups SET message_count = message_count + 1 WHERE group_id = ?", (group_id,))
            conn.commit()
            conn.close()
    
    def reset_message_count(self, group_id):
        """Reset message count for group"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE groups SET message_count = 0, last_drop = CURRENT_TIMESTAMP WHERE group_id = ?", (group_id,))
            conn.commit()
            conn.close()
    
    # CHARACTER MANAGEMENT
    def add_character(self, name, series_name, image_url, gender, added_by, rarity="Common"):
        """Add a new character to the database"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO characters (name, series_name, image_url, gender, added_by, rarity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, series_name, image_url, gender, added_by, rarity))
            
            character_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return character_id
    
    def get_character_by_id(self, character_id):
        """Get character information by ID"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
            character = cursor.fetchone()
            
            conn.close()
            return dict(character) if character else None
    
    def get_random_character(self, gender):
        """Get random character by gender (includes all characters)"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM characters WHERE gender = ? ORDER BY RANDOM() LIMIT 1", (gender,))
            character = cursor.fetchone()
            
            conn.close()
            return dict(character) if character else None
    
    def search_characters(self, query, limit=10):
        """Search characters by name or series"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM characters 
                WHERE name LIKE ? OR series_name LIKE ? 
                ORDER BY name LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            characters = cursor.fetchall()
            conn.close()
            return [dict(char) for char in characters]
    
    # COLLECTION MANAGEMENT
    def claim_character(self, user_id, character_id, group_id):
        """Claim a character for a user (allows duplicates with count increment)"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if user already has this character
            cursor.execute('''
                SELECT count FROM user_collections 
                WHERE user_id = ? AND character_id = ?
            ''', (user_id, character_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Increment count for existing character
                cursor.execute('''
                    UPDATE user_collections 
                    SET count = count + 1, last_claimed_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND character_id = ?
                ''', (user_id, character_id))
                new_count = existing[0] + 1
            else:
                # Add new character to collection
                cursor.execute('''
                    INSERT INTO user_collections (user_id, character_id, group_id, count)
                    VALUES (?, ?, ?, 1)
                ''', (user_id, character_id, group_id))
                new_count = 1
            
            conn.commit()
            conn.close()
            return new_count
    
    def get_user_collection(self, user_id, limit=None, offset=0):
        """Get user's character collection with counts"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT uc.id as collection_id, c.*, uc.count, uc.first_claimed_at, uc.last_claimed_at
                FROM user_collections uc
                JOIN characters c ON uc.character_id = c.id
                WHERE uc.user_id = ?
                ORDER BY uc.last_claimed_at DESC
            '''
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            cursor.execute(query, (user_id,))
            characters = cursor.fetchall()
            
            conn.close()
            return [dict(char) for char in characters]
    
    def get_collection_count(self, user_id):
        """Get total count of user's collection (including duplicates)"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*), SUM(count) FROM user_collections WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            unique_count = result[0] if result[0] else 0
            total_count = result[1] if result[1] else 0
            
            conn.close()
            return {"unique": unique_count, "total": total_count}
    
    def user_owns_character(self, user_id, character_id):
        """Check if user owns a character (always returns False to allow duplicates)"""
        return False  # Always allow duplicate catching
    
    def give_all_characters_to_user(self, user_id):
        """Give all characters to a special user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all characters
            cursor.execute("SELECT id FROM characters")
            characters = cursor.fetchall()
            
            for char in characters:
                character_id = char[0]
                # Check if user already has this character
                cursor.execute('''
                    SELECT id FROM user_collections 
                    WHERE user_id = ? AND character_id = ?
                ''', (user_id, character_id))
                
                if not cursor.fetchone():
                    # Add character to user's collection
                    cursor.execute('''
                        INSERT INTO user_collections (user_id, character_id, group_id, count)
                        VALUES (?, ?, -1, 1)
                    ''', (user_id, character_id))
            
            conn.commit()
            conn.close()
    
    # USER MANAGEMENT
    def add_special_user(self, user_id, username=None):
        """Add a special user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO special_users (user_id, username)
                VALUES (?, ?)
            ''', (user_id, username))
            
            conn.commit()
            conn.close()
    
    def remove_special_user(self, user_id):
        """Remove a special user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM special_users WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
    
    def is_special_user(self, user_id):
        """Check if user is special"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM special_users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
    
    def get_special_users(self):
        """Get all special users"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM special_users ORDER BY added_at DESC")
            users = cursor.fetchall()
            
            conn.close()
            return [dict(user) for user in users]
    
    def ban_user(self, user_id, username=None, reason=None):
        """Ban a user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO banned_users (user_id, username, reason)
                VALUES (?, ?, ?)
            ''', (user_id, username, reason))
            
            conn.commit()
            conn.close()
    
    def unban_user(self, user_id):
        """Unban a user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
    
    def is_banned(self, user_id):
        """Check if user is banned"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
    
    def get_banned_users(self):
        """Get all banned users"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM banned_users ORDER BY banned_at DESC")
            users = cursor.fetchall()
            
            conn.close()
            return [dict(user) for user in users]
    
    # DROP MANAGEMENT
    def create_drop(self, group_id, character_id, message_id=None):
        """Create an active drop"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO active_drops (group_id, character_id, message_id)
                VALUES (?, ?, ?)
            ''', (group_id, character_id, message_id))
            
            drop_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return drop_id
    
    def get_active_drop(self, group_id):
        """Get active drop for group"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ad.*, c.* FROM active_drops ad
                JOIN characters c ON ad.character_id = c.id
                WHERE ad.group_id = ?
                ORDER BY ad.created_at DESC LIMIT 1
            ''', (group_id,))
            
            drop = cursor.fetchone()
            conn.close()
            return dict(drop) if drop else None
    
    def remove_active_drop(self, group_id):
        """Remove active drop for group"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM active_drops WHERE group_id = ?", (group_id,))
            conn.commit()
            conn.close()
    
    # TRADING MANAGEMENT
    def create_trade(self, from_user_id, to_user_id, character_id, group_id):
        """Create a trade offer"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (from_user_id, to_user_id, character_id, group_id)
                VALUES (?, ?, ?, ?)
            ''', (from_user_id, to_user_id, character_id, group_id))
            
            trade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return trade_id
    
    def get_trade(self, trade_id):
        """Get trade information"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, c.name as character_name, c.series_name, c.image_url
                FROM trades t
                JOIN characters c ON t.character_id = c.id
                WHERE t.id = ?
            ''', (trade_id,))
            
            trade = cursor.fetchone()
            conn.close()
            return dict(trade) if trade else None
    
    def accept_trade(self, trade_id):
        """Accept a trade"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get trade details
            cursor.execute("SELECT * FROM trades WHERE id = ? AND status = 'pending'", (trade_id,))
            trade = cursor.fetchone()
            
            if not trade:
                conn.close()
                return False
            
            # Transfer character ownership
            cursor.execute('''
                UPDATE user_collections 
                SET user_id = ? 
                WHERE user_id = ? AND character_id = ?
            ''', (trade['to_user_id'], trade['from_user_id'], trade['character_id']))
            
            # Update trade status
            cursor.execute('''
                UPDATE trades 
                SET status = 'accepted', completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (trade_id,))
            
            conn.commit()
            conn.close()
            return True
    
    def reject_trade(self, trade_id):
        """Reject a trade"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades 
                SET status = 'rejected', completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (trade_id,))
            
            conn.commit()
            conn.close()
    
    def get_pending_trades(self, user_id):
        """Get pending trades for a user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, c.name as character_name, c.series_name
                FROM trades t
                JOIN characters c ON t.character_id = c.id
                WHERE t.to_user_id = ? AND t.status = 'pending'
                ORDER BY t.created_at DESC
            ''', (user_id,))
            
            trades = cursor.fetchall()
            conn.close()
            return [dict(trade) for trade in trades]

# Create global database instance
db = Database()