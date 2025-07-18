import random
from database import db
from config import RARITY_WEIGHTS, SUMMON_COST, RARITY_COLORS
from characters import populate_characters

class GachaSystem:
    def __init__(self):
        # Ensure characters are populated
        populate_characters()
    
    def calculate_weighted_rarity(self):
        """Calculate rarity based on weighted random selection"""
        rarities = list(RARITY_WEIGHTS.keys())
        weights = list(RARITY_WEIGHTS.values())
        
        return random.choices(rarities, weights=weights, k=1)[0]
    
    def summon_character(self, user_id):
        """Summon a character for the user"""
        # Check if user has enough coins
        user = db.get_user(user_id)
        if not user or user['coins'] < SUMMON_COST:
            return None, "Insufficient coins! You need {} coins to summon.".format(SUMMON_COST)
        
        # Deduct coins
        new_balance = user['coins'] - SUMMON_COST
        db.update_user_coins(user_id, new_balance)
        
        # Determine rarity
        rarity = self.calculate_weighted_rarity()
        
        # Get random character of that rarity
        character = db.get_random_character_by_rarity(rarity)
        
        if not character:
            # Refund coins if no character found
            db.update_user_coins(user_id, user['coins'])
            return None, "No characters available for summoning. Please try again later."
        
        # Add character to user's inventory
        db.add_character_to_user(user_id, character['id'])
        
        # Create result message
        rarity_icon = RARITY_COLORS.get(rarity, "⚪")
        result_msg = f"""
🎉 **SUMMON SUCCESSFUL!** 🎉

{rarity_icon} **{character['name']}** {rarity_icon}
📺 Anime: {character['anime']}
⭐ Rarity: {rarity}
💰 Coins remaining: {new_balance}

{character['description']}
"""
        
        return character, result_msg
    
    def get_summon_statistics(self, user_id):
        """Get user's summoning statistics"""
        user = db.get_user(user_id)
        stats = db.get_user_stats(user_id)
        
        if not user:
            return "User not found."
        
        msg = f"""
📊 **SUMMONING STATISTICS** 📊

👤 Player: {user['first_name']}
💰 Coins: {user['coins']}
🎲 Total Summons: {user['total_summons']}
🗂️ Total Characters: {stats['total_characters']}

**Collection by Rarity:**
"""
        
        for rarity in ['Legendary', 'Epic', 'Rare', 'Uncommon', 'Common']:
            count = stats['rarity_breakdown'].get(rarity, 0)
            icon = RARITY_COLORS.get(rarity, "⚪")
            msg += f"{icon} {rarity}: {count}\n"
        
        return msg
    
    def multi_summon(self, user_id, count=5):
        """Perform multiple summons at once"""
        user = db.get_user(user_id)
        total_cost = SUMMON_COST * count
        
        if not user or user['coins'] < total_cost:
            return None, f"Insufficient coins! You need {total_cost} coins for {count} summons."
        
        results = []
        for i in range(count):
            character, msg = self.summon_character(user_id)
            if character:
                results.append(character)
        
        if not results:
            return None, "No characters were summoned. Please try again."
        
        # Create summary message
        summary_msg = f"🎊 **{count}x SUMMON RESULTS** 🎊\n\n"
        
        rarity_counts = {}
        for char in results:
            rarity = char['rarity']
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        for rarity, count in rarity_counts.items():
            icon = RARITY_COLORS.get(rarity, "⚪")
            summary_msg += f"{icon} {rarity}: {count}\n"
        
        summary_msg += f"\n💰 Coins remaining: {db.get_user(user_id)['coins']}"
        
        return results, summary_msg

# Global gacha system instance
gacha = GachaSystem()
