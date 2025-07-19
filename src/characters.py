from database import db

# Sample characters for the waifu/husbando bot
SAMPLE_CHARACTERS = [
    # Waifus
    {
        'name': 'Zero Two',
        'series_name': 'Darling in the FranXX',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/darling-in-the-franxx/images/4/4e/Zero_Two_anime.png',
        'rarity': 'Legendary'
    },
    {
        'name': 'Nezuko Kamado',
        'series_name': 'Demon Slayer',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/kimetsu-no-yaiba/images/7/75/Nezuko_anime_design.png',
        'rarity': 'Epic'
    },
    {
        'name': 'Mikasa Ackerman',
        'series_name': 'Attack on Titan',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/shingekinokyojin/images/4/4c/Mikasa_Ackerman_%28Anime%29_character_image.png',
        'rarity': 'Epic'
    },
    {
        'name': 'Marin Kitagawa',
        'series_name': 'My Dress-Up Darling',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/sono-bisque-doll-wa-koi-wo-suru/images/1/1f/Marin_Kitagawa_anime_design.png',
        'rarity': 'Rare'
    },
    {
        'name': 'Rem',
        'series_name': 'Re:Zero',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/rezero/images/8/8c/Rem_anime_design.png',
        'rarity': 'Legendary'
    },
    {
        'name': 'Tohru Honda',
        'series_name': 'Fruits Basket',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/fruitsbasket/images/2/2c/Tohru_Honda_2019.png',
        'rarity': 'Common'
    },
    {
        'name': 'Violet Evergarden',
        'series_name': 'Violet Evergarden',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/violet-evergarden/images/5/5a/Violet_Evergarden_anime_design.png',
        'rarity': 'Epic'
    },
    {
        'name': 'Asuna Yuuki',
        'series_name': 'Sword Art Online',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/swordartonline/images/f/f8/Asuna_ALO_anime_design.png',
        'rarity': 'Rare'
    },
    {
        'name': 'Hinata Hyuga',
        'series_name': 'Naruto',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/naruto/images/7/7b/Hinata_Hyuga_anime_design.png',
        'rarity': 'Uncommon'
    },
    {
        'name': 'Ochaco Uraraka',
        'series_name': 'My Hero Academia',
        'gender': 'waifu',
        'image_url': 'https://static.wikia.nocookie.net/bokunoheroacademia/images/9/9c/Ochaco_Uraraka_anime_design.png',
        'rarity': 'Common'
    },
    
    # Husbandos
    {
        'name': 'Tanjiro Kamado',
        'series_name': 'Demon Slayer',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/kimetsu-no-yaiba/images/9/99/Tanjiro_anime_design.png',
        'rarity': 'Epic'
    },
    {
        'name': 'Levi Ackerman',
        'series_name': 'Attack on Titan',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/shingekinokyojin/images/2/2c/Levi_Ackerman_%28Anime%29_character_image.png',
        'rarity': 'Legendary'
    },
    {
        'name': 'Gojo Satoru',
        'series_name': 'Jujutsu Kaisen',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/jujutsu-kaisen/images/5/5a/Satoru_Gojo_anime_design.png',
        'rarity': 'Legendary'
    },
    {
        'name': 'Izuku Midoriya',
        'series_name': 'My Hero Academia',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/bokunoheroacademia/images/1/1f/Izuku_Midoriya_anime_design.png',
        'rarity': 'Rare'
    },
    {
        'name': 'Naruto Uzumaki',
        'series_name': 'Naruto',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/naruto/images/d/dd/Naruto_anime_design.png',
        'rarity': 'Epic'
    },
    {
        'name': 'Edward Elric',
        'series_name': 'Fullmetal Alchemist',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/fma/images/5/5c/Edward_Elric_anime_design.png',
        'rarity': 'Rare'
    },
    {
        'name': 'Kirito',
        'series_name': 'Sword Art Online',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/swordartonline/images/f/f8/Kirito_ALO_anime_design.png',
        'rarity': 'Uncommon'
    },
    {
        'name': 'Senku Ishigami',
        'series_name': 'Dr. Stone',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/dr-stone/images/d/d5/Senku_Ishigami_anime_design.png',
        'rarity': 'Common'
    },
    {
        'name': 'Yusuke Urameshi',
        'series_name': 'Yu Yu Hakusho',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/yuyuhakusho/images/f/f8/Yusuke_anime_design.png',
        'rarity': 'Uncommon'
    },
    {
        'name': 'Ichigo Kurosaki',
        'series_name': 'Bleach',
        'gender': 'husbando',
        'image_url': 'https://static.wikia.nocookie.net/bleach/images/f/f8/Ichigo_Kurosaki_anime_design.png',
        'rarity': 'Rare'
    }
]

def populate_characters():
    """Initialize character database (no longer auto-populates sample characters)"""
    print("🎭 Character database initialized - ready for character drops!")
    print("📊 All characters (user-added and system) available for drops")

if __name__ == "__main__":
    populate_characters()