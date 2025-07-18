import sqlite3
import threading
from datetime import datetime, timedelta
from config import DATABASE_PATH

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
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    coins INTEGER DEFAULT 100,
                    last_daily TIMESTAMP,
                    total_summons INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Characters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    anime TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    image_url TEXT,
                    description TEXT,
                    type TEXT CHECK(type IN ('waifu', 'husbando')) NOT NULL
                )
            ''')
            
            # User characters (inventory)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    character_id INTEGER,
                    obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (character_id) REFERENCES characters (id)
                )
            ''')
            
            # Trading table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER,
                    to_user_id INTEGER,
                    from_character_id INTEGER,
                    to_character_id INTEGER,
                    status TEXT CHECK(status IN ('pending', 'accepted', 'rejected', 'cancelled')) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (from_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (to_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (from_character_id) REFERENCES user_characters (id),
                    FOREIGN KEY (to_character_id) REFERENCES user_characters (id)
                )
            ''')
            
            # Daily rewards tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_rewards (
                    user_id INTEGER,
                    last_claim TIMESTAMP,
                    streak INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def register_user(self, user_id, username, first_name):
        """Register a new user or update existing user info"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, coins, created_at)
                VALUES (?, ?, ?, 
                    COALESCE((SELECT coins FROM users WHERE user_id = ?), 100),
                    COALESCE((SELECT created_at FROM users WHERE user_id = ?), CURRENT_TIMESTAMP))
            ''', (user_id, username, first_name, user_id, user_id))
            
            conn.commit()
            conn.close()
    
    def get_user(self, user_id):
        """Get user information"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            conn.close()
            return dict(user) if user else None
    
    def update_user_coins(self, user_id, coins):
        """Update user's coin balance"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (coins, user_id))
            conn.commit()
            conn.close()
    
    def add_character_to_user(self, user_id, character_id):
        """Add a character to user's inventory"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_characters (user_id, character_id)
                VALUES (?, ?)
            ''', (user_id, character_id))
            
            cursor.execute("UPDATE users SET total_summons = total_summons + 1 WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
    
    def get_user_characters(self, user_id, limit=None, offset=0):
        """Get user's character collection"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT uc.id as user_char_id, c.*, uc.obtained_at
                FROM user_characters uc
                JOIN characters c ON uc.character_id = c.id
                WHERE uc.user_id = ?
                ORDER BY uc.obtained_at DESC
            '''
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            cursor.execute(query, (user_id,))
            characters = cursor.fetchall()
            
            conn.close()
            return [dict(char) for char in characters]
    
    def get_character_by_id(self, character_id):
        """Get character information by ID"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
            character = cursor.fetchone()
            
            conn.close()
            return dict(character) if character else None
    
    def get_random_character_by_rarity(self, rarity):
        """Get a random character of specific rarity"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM characters 
                WHERE rarity = ? 
                ORDER BY RANDOM() 
                LIMIT 1
            ''', (rarity,))
            
            character = cursor.fetchone()
            conn.close()
            return dict(character) if character else None
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get total characters
            cursor.execute("SELECT COUNT(*) FROM user_characters WHERE user_id = ?", (user_id,))
            total_chars = cursor.fetchone()[0]
            
            # Get characters by rarity
            cursor.execute('''
                SELECT c.rarity, COUNT(*) as count
                FROM user_characters uc
                JOIN characters c ON uc.character_id = c.id
                WHERE uc.user_id = ?
                GROUP BY c.rarity
            ''', (user_id,))
            
            rarity_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            return {
                'total_characters': total_chars,
                'rarity_breakdown': rarity_counts
            }
    
    def can_claim_daily_reward(self, user_id):
        """Check if user can claim daily reward"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT last_claim FROM daily_rewards 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return True
            
            last_claim = datetime.fromisoformat(result[0])
            return datetime.now() - last_claim >= timedelta(days=1)
    
    def claim_daily_reward(self, user_id):
        """Claim daily reward for user"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Update or insert daily reward record
            cursor.execute('''
                INSERT OR REPLACE INTO daily_rewards (user_id, last_claim, streak)
                VALUES (?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT streak FROM daily_rewards WHERE user_id = ?), 0) + 1)
            ''', (user_id, user_id))
            
            # Add coins to user
            cursor.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (50, user_id))
            
            conn.commit()
            conn.close()

# Global database instance
db = Database()
