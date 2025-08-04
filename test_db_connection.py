import mysql.connector
from configparser import ConfigParser

def test_connection():
    config = ConfigParser()
    config.read("config.ini")

    try:
        conn = mysql.connector.connect(
            host=config['mysql']['host'],
            user=config['mysql']['user'],
            password=config['mysql']['password'],
            database=config['mysql']['database']
        )
        print("✅ Connected to MySQL database successfully.")
        conn.close()
    except mysql.connector.Error as err:
        print(f"❌ Connection failed: {err}")

if __name__ == "__main__":
    test_connection()
