import mysql.connector
import logging
from log_parser import parse_log_file

# ✅ Password updated here
DB_CONFIG = {
    'user': 'root',
    'password': '12345',  # ⬅️ your password
    'host': 'localhost',
    'database': 'weblogs_db',
}

def insert_logs_to_db(entries):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO weblogs (
            ip_address, timestamp, method, path, protocol,
            status_code, bytes_sent, referrer, user_agent
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for entry in entries:
            try:
                cursor.execute(insert_query, (
                    entry['ip_address'],
                    entry['timestamp'],
                    entry['method'],
                    entry['path'],
                    entry['protocol'],
                    entry['status_code'],
                    entry['bytes_sent'],
                    entry['referrer'],
                    entry['user_agent'],
                ))
            except Exception as e:
                logging.warning(f"Failed to insert entry: {entry}\nError: {e}")

        conn.commit()
        print(f"✅ Inserted {cursor.rowcount} entries.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        logging.error(f"MySQL error: {err}")

if __name__ == "__main__":
    log_file = "sample_logs/sample_access.log"  # ✅ Make sure this file exists
    parsed_entries = parse_log_file(log_file)
    insert_logs_to_db(parsed_entries)
