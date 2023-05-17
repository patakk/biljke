import sqlite3


def create_connection(db_file):
    db_connection = None
    try:
        db_connection = sqlite3.connect(db_file)
        return db_connection
    
    except sqlite3.Error as db_error:
        print(db_error)
    
    return db_connection


CONNECTION = create_connection('biljke.db')
CURSOR = CONNECTION.cursor()


def create_tables():
    # Create plants table
    CURSOR.execute("""
    CREATE TABLE IF NOT EXISTS plants (
        plant_id INTEGER PRIMARY KEY,
        plant_name TEXT NOT NULL,
        plant_photo TEXT NOT NULL,
        plant_optimal_ph FLOAT NOT NULL,
        plant_optimal_salinity FLOAT NOT NULL,
        plant_min_temp FLOAT NOT NULL,
        plant_max_temp FLOAT NOT NULL,
        plant_min_soil_moisture FLOAT NULL,
        plant_needed_light_level FLOAT NOT NULL
    )
    """)

    # Create pots table
    CURSOR.execute("""
    CREATE TABLE IF NOT EXISTS pots (
        pot_id INTEGER PRIMARY KEY,
        plant_id INTEGER,
        pot_ph TEXT NOT NULL,
        pot_salinity TEXT NOT NULL,
        pot_temp TEXT NOT NULL,
        pot_soil_moisture TEXT NULL,
        pot_light_level TEXT NOT NULL
    )
    """)

    # Create users table
    CURSOR.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL,
        user_password TEXT NOT NULL,
        user_pots TEXT
    )
    """)

    # Commit the changes
    CONNECTION.commit()

def populateDatabase():
    # Insert sample data into plants table
    plants = [
        (1, 'Suncokret', 6.0, 10.0, 10.0, 30.0, 10.0, 10.0, 'sunflower.png'),
        (2, 'Tulipan', 6.5, 8.0, 5.0, 25.0, 8.0, 6.0, 'tulip.png'),
        (3, 'Ruža', 6.0, 6.0, 15.0, 25.0, 6.0, 8.0, 'rose.png'),
    ]

    for plant in plants:
        CURSOR.execute("""
        INSERT OR IGNORE INTO plants (plant_id, plant_name, plant_optimal_ph, plant_optimal_salinity, plant_min_temp, plant_max_temp, plant_min_soil_moisture, plant_needed_light_level, plant_photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, plant)

    # Insert sample data into pots table
    pots = [
        (1, 1, '6.0', '10.0', '20.0', '10.0', '10.0'),
        (2, 2, '6.5', '8.0', '15.0', '8.0', '6.0'),
        (3, 3, '6.0', '6.0', '18.0', '6.0', '8.0'),
        (4, 1, '6.2', '9.0', '22.0', '9.0', '9.0'),
        (5, 2, '6.3', '7.5', '17.0', '7.0', '5.5'),
        (6, 2, '6.5', '7.0', '20.0', '8.0', '6.0'),
    ]

    for pot in pots:
        CURSOR.execute("""
        INSERT OR IGNORE INTO pots (pot_id, plant_id, pot_ph, pot_salinity, pot_temp, pot_soil_moisture, pot_light_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, pot)

    # Insert sample data into users table
    users = [
        ('user1', 'pass1', '1,2'),
        ('user2', 'pass2', '3,4,5'),
        ('user3', 'pass3', '6'),
    ]

    for user in users:
        CURSOR.execute("""
        INSERT OR IGNORE INTO users (user_name, user_password, user_pots)
        VALUES (?, ?, ?)
        """, user)

    # Commit the changes
    CONNECTION.commit()

if __name__ == '__main__':
    create_tables()
    populateDatabase()
    CURSOR.close()
    CONNECTION.close()

