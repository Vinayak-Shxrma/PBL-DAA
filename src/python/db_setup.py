import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'smart_routes'
}

def create_database():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS smart_routes")
        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Database creation failed: {err}")
    finally:
        conn.close()

def create_table():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS highways (
                city1 VARCHAR(100),
                city2 VARCHAR(100),
                distance FLOAT,
                PRIMARY KEY (city1, city2)
            )
        ''')
        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Table creation failed: {err}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()
    create_table()
