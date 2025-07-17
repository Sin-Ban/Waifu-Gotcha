from database import db
from config import RARITY_MULTIPLIERS, MAX_TRADES_PER_DAY
from datetime import datetime, timedelta

class TradingSystem:
    def __init__(self):
        pass
    
    def get_character_value(self, character):
        """Calculate character trading value based on rarity"""
        base_value = RARITY_MULTIPLIERS.get(character['rarity'], 1)
        return base_value
    
    def can_user_trade(self, user_id):
        """Check if user can initiate more trades today"""
        # For simplicity, we'll allow unlimited trades
        # In a real implementation, you'd track daily trade limits
        return True
    
    def propose_trade(self, from_user_id, to_user_id, from_char_id, to_char_id):
        """Propose a trade between two users"""
        # Get user characters
        from_chars = db.get_user_characters(from_user_id)
        to_chars = db.get_user_characters(to_user_id)
        
        # Find the specific characters
        from_char = next((c for c in from_chars if c['user_char_id'] == from_char_id), None)
        to_char = next((c for c in to_chars if c['user_char_id'] == to_char_id), None)
        
        if not from_char or not to_char:
            return False, "One or both characters not found in user inventories."
        
        # Check if users can trade
        if not self.can_user_trade(from_user_id):
            return False, "You have reached your daily trading limit."
        
        # Store trade proposal in database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (from_user_id, to_user_id, from_character_id, to_character_id, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (from_user_id, to_user_id, from_char_id, to_char_id))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return True, f"Trade proposal #{trade_id} sent successfully!"
    
    def accept_trade(self, trade_id, user_id):
        """Accept a trade proposal"""
        # Get trade details
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE id = ? AND to_user_id = ? AND status = 'pending'
        ''', (trade_id, user_id))
        
        trade = cursor.fetchone()
        if not trade:
            conn.close()
            return False, "Trade not found or already completed."
        
        # Execute the trade
        try:
            # Update character ownership
            cursor.execute('''
                UPDATE user_characters 
                SET user_id = ? 
                WHERE id = ?
            ''', (trade['to_user_id'], trade['from_character_id']))
            
            cursor.execute('''
                UPDATE user_characters 
                SET user_id = ? 
                WHERE id = ?
            ''', (trade['from_user_id'], trade['to_character_id']))
            
            # Update trade status
            cursor.execute('''
                UPDATE trades 
                SET status = 'accepted', completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (trade_id,))
            
            conn.commit()
            conn.close()
            
            return True, f"Trade #{trade_id} completed successfully!"
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Trade failed: {str(e)}"
    
    def reject_trade(self, trade_id, user_id):
        """Reject a trade proposal"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE trades 
            SET status = 'rejected', completed_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND to_user_id = ? AND status = 'pending'
        ''', (trade_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return False, "Trade not found or already completed."
        
        conn.commit()
        conn.close()
        
        return True, f"Trade #{trade_id} rejected."
    
    def get_pending_trades(self, user_id):
        """Get all pending trades for a user"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, 
                   c1.name as from_char_name, c1.anime as from_char_anime, c1.rarity as from_char_rarity,
                   c2.name as to_char_name, c2.anime as to_char_anime, c2.rarity as to_char_rarity,
                   u1.first_name as from_user_name, u2.first_name as to_user_name
            FROM trades t
            JOIN user_characters uc1 ON t.from_character_id = uc1.id
            JOIN user_characters uc2 ON t.to_character_id = uc2.id
            JOIN characters c1 ON uc1.character_id = c1.id
            JOIN characters c2 ON uc2.character_id = c2.id
            JOIN users u1 ON t.from_user_id = u1.user_id
            JOIN users u2 ON t.to_user_id = u2.user_id
            WHERE (t.from_user_id = ? OR t.to_user_id = ?) AND t.status = 'pending'
            ORDER BY t.created_at DESC
        ''', (user_id, user_id))
        
        trades = cursor.fetchall()
        conn.close()
        
        return [dict(trade) for trade in trades]
    
    def get_trade_history(self, user_id, limit=10):
        """Get user's trade history"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, 
                   c1.name as from_char_name, c1.rarity as from_char_rarity,
                   c2.name as to_char_name, c2.rarity as to_char_rarity,
                   u1.first_name as from_user_name, u2.first_name as to_user_name
            FROM trades t
            JOIN user_characters uc1 ON t.from_character_id = uc1.id
            JOIN user_characters uc2 ON t.to_character_id = uc2.id
            JOIN characters c1 ON uc1.character_id = c1.id
            JOIN characters c2 ON uc2.character_id = c2.id
            JOIN users u1 ON t.from_user_id = u1.user_id
            JOIN users u2 ON t.to_user_id = u2.user_id
            WHERE (t.from_user_id = ? OR t.to_user_id = ?) AND t.status != 'pending'
            ORDER BY t.completed_at DESC
            LIMIT ?
        ''', (user_id, user_id, limit))
        
        trades = cursor.fetchall()
        conn.close()
        
        return [dict(trade) for trade in trades]

# Global trading system instance
trading = TradingSystem()
