import sqlite3
from config import DATABASE_PATH

# Pre-defined anime characters with their details
ANIME_CHARACTERS = [
    # Legendary Waifus
    ("Rem", "Re:Zero", "Legendary", "https://pixabay.com/get/g657ca7070bf82648906e8979051bb86f2d7c4fb4f663f57c43af2d8134835b4b035b0fd2e968b28d8db5e35f05d8906cd10f6d75c32474b4a51bca0c2d476238_1280.jpg", "Blue-haired oni maid devoted to Subaru", "waifu"),
    ("Mikasa Ackerman", "Attack on Titan", "Legendary", "https://pixabay.com/get/gdde39eaba5387cae174c08ae16e6bdbfc4640ad5d547f57425df35bb95c2a5f65ab45e1ebc221643f95889a5f7aee6ffadf24830e3c32ad36c372344a731e635_1280.jpg", "Elite soldier with incredible combat skills", "waifu"),
    ("Nezuko Kamado", "Demon Slayer", "Legendary", "https://pixabay.com/get/gc05d8292f43e90a2bfa48437de14e2782597eb6e0ac0a002d8d48bbe5ff29ceaae7a56d17c3be6fe2d242af152841536b1652e66095ac52f136da946b1d20e68_1280.jpg", "Demon girl who protects humans", "waifu"),
    ("Zero Two", "Darling in the FranXX", "Legendary", "https://pixabay.com/get/gd0a0e7b826d9901f737fc2367617dbd3b56345fbf958643c6c382d8a168dc5a36829bd98fa91b85edad9b227670bb0dfba06ea5aec6243c3ad9a801a12fc1189_1280.jpg", "Half-human, half-klaxosaur pilot", "waifu"),
    
    # Legendary Husbandos
    ("Levi Ackerman", "Attack on Titan", "Legendary", "https://pixabay.com/get/g821661df0fb89365f252b7a16674cd54dc68386573174c24bdf49d89e26a4c3059c6e8e42476090103756579df11e6f8d7f852304227752735ba017efed97cf6_1280.jpg", "Humanity's strongest soldier", "husbando"),
    ("Tomioka Giyu", "Demon Slayer", "Legendary", "https://pixabay.com/get/ge23beb7794b4f29e23bb7d6b4f52436be3c058103663d37084979f24f2c3937dc8d5301ebecb5100994e75931c274f9512f4f4718b4ad93a31b48ec676626fe7_1280.jpg", "Water Hashira with calm demeanor", "husbando"),
    
    # Epic Characters
    ("Megumin", "KonoSuba", "Epic", "https://pixabay.com/get/g34bcc555df769a458250d4ab1544db02a5318258faff191e58a0d19d46af9bc11e4bfe21d07236d61c5f389c12a1eaaac47086223d0d66bd5d88b8082e04e57c_1280.jpg", "Explosion magic enthusiast", "waifu"),
    ("Inosuke Hashibira", "Demon Slayer", "Epic", "https://pixabay.com/get/g8f2ef3af491a9375e51c5280e8e199b7ef9296c4e427e86d804daf47a02922a91965096fad9bbce991c7254c825926097d31a6bf201cf7dfca0afa02e256bc8b_1280.jpg", "Beast Breathing user", "husbando"),
    ("Raphtalia", "Rising of the Shield Hero", "Epic", "https://pixabay.com/get/g7b60583e6ad46b0f93d183a0c7a96220966b87f95c4d365fc1b1824aabb377e65ecf77433b0530d9606257425f8d9a2813a77062c6d33bb1da246f2ba93f82f2_1280.jpg", "Raccoon demi-human warrior", "waifu"),
    ("Senku Ishigami", "Dr. Stone", "Epic", "https://pixabay.com/get/g4dcb2431bbf20c07a3c119b2f099e0f21d25a61e188bc962de07d67c82fcc51a9d8e21485e85aee6f1427b92e7f46f3babab65e2bed40a67eb25d95218a94994_1280.jpg", "Genius scientist rebuilding civilization", "husbando"),
    
    # Rare Characters
    ("Aqua", "KonoSuba", "Rare", "https://pixabay.com/get/gbc1d78466dfb17bc9d9c774dfe7791cf78807c03b36987dba08d291c2e65d293b8c2d2e5fcbc88bee52609b6139bbac4137b3f42129125d56cdd7809fcae0404_1280.jpg", "Water goddess with questionable wisdom", "waifu"),
    ("Zenitsu Agatsuma", "Demon Slayer", "Rare", "https://pixabay.com/get/g3b3bb83ea2a7c83830a51012c1f264139ac53727124f1357d4ddb87123783f2695256f026975297d33754803329241cf44f06aa919e9c0d7f50fe956af3e4493_1280.jpg", "Thunder Breathing user", "husbando"),
    ("Emilia", "Re:Zero", "Rare", "https://pixabay.com/get/g657ca7070bf82648906e8979051bb86f2d7c4fb4f663f57c43af2d8134835b4b035b0fd2e968b28d8db5e35f05d8906cd10f6d75c32474b4a51bca0c2d476238_1280.jpg", "Half-elf with ice magic", "waifu"),
    ("Kazuma Sato", "KonoSuba", "Rare", "https://pixabay.com/get/gdde39eaba5387cae174c08ae16e6bdbfc4640ad5d547f57425df35bb95c2a5f65ab45e1ebc221643f95889a5f7aee6ffadf24830e3c32ad36c372344a731e635_1280.jpg", "Lazy but cunning adventurer", "husbando"),
    
    # Uncommon Characters
    ("Darkness", "KonoSuba", "Uncommon", "https://pixabay.com/get/gc05d8292f43e90a2bfa48437de14e2782597eb6e0ac0a002d8d48bbe5ff29ceaae7a56d17c3be6fe2d242af152841536b1652e66095ac52f136da946b1d20e68_1280.jpg", "Masochistic crusader", "waifu"),
    ("Tanjiro Kamado", "Demon Slayer", "Uncommon", "https://pixabay.com/get/gd0a0e7b826d9901f737fc2367617dbd3b56345fbf958643c6c382d8a168dc5a36829bd98fa91b85edad9b227670bb0dfba06ea5aec6243c3ad9a801a12fc1189_1280.jpg", "Kind-hearted demon slayer", "husbando"),
    ("Hinata Hyuga", "Naruto", "Uncommon", "https://pixabay.com/get/g821661df0fb89365f252b7a16674cd54dc68386573174c24bdf49d89e26a4c3059c6e8e42476090103756579df11e6f8d7f852304227752735ba017efed97cf6_1280.jpg", "Shy but determined ninja", "waifu"),
    ("Sasuke Uchiha", "Naruto", "Uncommon", "https://pixabay.com/get/ge23beb7794b4f29e23bb7d6b4f52436be3c058103663d37084979f24f2c3937dc8d5301ebecb5100994e75931c274f9512f4f4718b4ad93a31b48ec676626fe7_1280.jpg", "Avenger seeking power", "husbando"),
    
    # Common Characters
    ("Sakura Haruno", "Naruto", "Common", "https://pixabay.com/get/g34bcc555df769a458250d4ab1544db02a5318258faff191e58a0d19d46af9bc11e4bfe21d07236d61c5f389c12a1eaaac47086223d0d66bd5d88b8082e04e57c_1280.jpg", "Medical ninja with strong punches", "waifu"),
    ("Naruto Uzumaki", "Naruto", "Common", "https://pixabay.com/get/g8f2ef3af491a9375e51c5280e8e199b7ef9296c4e427e86d804daf47a02922a91965096fad9bbce991c7254c825926097d31a6bf201cf7dfca0afa02e256bc8b_1280.jpg", "Energetic ninja with nine-tailed fox", "husbando"),
    ("Ochaco Uraraka", "My Hero Academia", "Common", "https://pixabay.com/get/g7b60583e6ad46b0f93d183a0c7a96220966b87f95c4d365fc1b1824aabb377e65ecf77433b0530d9606257425f8d9a2813a77062c6d33bb1da246f2ba93f82f2_1280.jpg", "Gravity-manipulating hero student", "waifu"),
    ("Deku", "My Hero Academia", "Common", "https://pixabay.com/get/g4dcb2431bbf20c07a3c119b2f099e0f21d25a61e188bc962de07d67c82fcc51a9d8e21485e85aee6f1427b92e7f46f3babab65e2bed40a67eb25d95218a94994_1280.jpg", "Quirkless boy who becomes a hero", "husbando"),
    ("Momo Yaoyorozu", "My Hero Academia", "Common", "https://pixabay.com/get/gbc1d78466dfb17bc9d9c774dfe7791cf78807c03b36987dba08d291c2e65d293b8c2d2e5fcbc88bee52609b6139bbac4137b3f42129125d56cdd7809fcae0404_1280.jpg", "Creation quirk user", "waifu"),
    ("Todoroki Shoto", "My Hero Academia", "Common", "https://pixabay.com/get/g3b3bb83ea2a7c83830a51012c1f264139ac53727124f1357d4ddb87123783f2695256f026975297d33754803329241cf44f06aa919e9c0d7f50fe956af3e4493_1280.jpg", "Half-hot, half-cold quirk user", "husbando"),
]

def populate_characters():
    """Populate the database with anime characters"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if characters are already populated
    cursor.execute("SELECT COUNT(*) FROM characters")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany('''
            INSERT INTO characters (name, anime, rarity, image_url, description, type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ANIME_CHARACTERS)
        
        conn.commit()
        print(f"Populated database with {len(ANIME_CHARACTERS)} characters")
    
    conn.close()

def get_character_count_by_rarity():
    """Get count of characters by rarity for balancing"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rarity, COUNT(*) as count
        FROM characters
        GROUP BY rarity
    ''')
    
    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    return result

if __name__ == "__main__":
    populate_characters()
    print("Character counts by rarity:", get_character_count_by_rarity())
