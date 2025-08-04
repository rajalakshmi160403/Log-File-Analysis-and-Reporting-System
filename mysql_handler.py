import mysql.connector
from configparser import ConfigParser
from datetime import datetime
from collections import Counter
from user_agents import parse as parse_ua  # ✅ required for parsing user agent strings


class MySQLHandler:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_agents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_agent_string TEXT UNIQUE
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45),
            timestamp DATETIME,
            method VARCHAR(10),
            path TEXT,
            status_code INT,
            bytes_sent INT,
            referrer TEXT,
            user_agent_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_agent_id) REFERENCES user_agents(id),
            UNIQUE(ip_address, timestamp, path)
        )
        ''')

        self.conn.commit()

    def insert_user_agent(self, user_agent_string):
        if not user_agent_string:
            return None

        query = '''
        INSERT IGNORE INTO user_agents (user_agent_string)
        VALUES (%s)
        '''
        self.cursor.execute(query, (user_agent_string,))
        self.conn.commit()

        self.cursor.execute("SELECT id FROM user_agents WHERE user_agent_string = %s", (user_agent_string,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def insert_log_entry(self, entry):
        user_agent_id = self.insert_user_agent(entry['user_agent'])
        timestamp = entry['timestamp']

        query = '''
        INSERT IGNORE INTO log_entries (
            ip_address, timestamp, method, path, status_code,
            bytes_sent, referrer, user_agent_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        self.cursor.execute(query, (
            entry['ip_address'],
            timestamp,
            entry['method'],
            entry['path'],
            entry['status_code'],
            entry['bytes_sent'],
            entry['referrer'],
            user_agent_id
        ))
        self.conn.commit()

    def insert_batch_log_entries(self, entries):
        user_agents = {}
        log_rows = []

        for entry in entries:
            ua = entry['user_agent']

            if ua not in user_agents:
                self.cursor.execute('''
                    INSERT IGNORE INTO user_agents (user_agent_string)
                    VALUES (%s)
                ''', (ua,))
                self.conn.commit()

                self.cursor.execute("SELECT id FROM user_agents WHERE user_agent_string = %s", (ua,))
                result = self.cursor.fetchone()
                user_agents[ua] = result[0] if result else None

            user_agent_id = user_agents[ua]

            log_rows.append((
                entry['ip_address'],
                entry['timestamp'],
                entry['method'],
                entry['path'],
                entry['status_code'],
                entry['bytes_sent'],
                entry['referrer'],
                user_agent_id
            ))

        self.cursor.executemany('''
            INSERT IGNORE INTO log_entries (
                ip_address, timestamp, method, path, status_code,
                bytes_sent, referrer, user_agent_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', log_rows)
        self.conn.commit()

    def get_top_n_ips(self, n):
        self.cursor.execute('''
        SELECT ip_address, COUNT(*) AS request_count
        FROM log_entries
        GROUP BY ip_address
        ORDER BY request_count DESC
        LIMIT %s
        ''', (n,))
        return self.cursor.fetchall()

    def get_status_code_distribution(self):
        self.cursor.execute('''
        SELECT status_code, COUNT(*) AS count
        FROM log_entries
        GROUP BY status_code
        ''')
        results = self.cursor.fetchall()
        total = sum(count for _, count in results)
        return [(code, count, f"{(count / total) * 100:.1f}%") for code, count in results]

    def get_hourly_traffic(self):
        self.cursor.execute('''
        SELECT HOUR(timestamp) AS hour, COUNT(*) AS request_count
        FROM log_entries
        GROUP BY hour
        ORDER BY hour
        ''')
        return self.cursor.fetchall()

    def get_error_logs_by_date(self, date_str):
        self.cursor.execute('''
        SELECT ip_address, timestamp, method, path, status_code
        FROM log_entries
        WHERE DATE(timestamp) = %s
        AND status_code >= 400
        ORDER BY timestamp
        ''', (date_str,))
        return self.cursor.fetchall()

    def get_traffic_by_os(self):
        self.cursor.execute('''
        SELECT ua.user_agent_string
        FROM log_entries le
        JOIN user_agents ua ON le.user_agent_id = ua.id
        ''')
        rows = self.cursor.fetchall()

        os_counter = Counter()
        for (ua_string,) in rows:
            if ua_string:
                try:
                    parsed = parse_ua(ua_string)
                    os_name = parsed.os.family
                    os_counter[os_name] += 1
                except Exception:
                    os_counter["Unknown"] += 1

        return os_counter.most_common()

    def close(self):
        self.cursor.close()
        self.conn.close()
