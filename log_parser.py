import re
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO)

# Apache combined log regex
log_pattern = re.compile(
    r'(?P<ip>\S+) - - \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status_code>\d{3}) (?P<response_size>\d+|-) '
    r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
)

def parse_log_line(line):
    match = log_pattern.match(line.strip())
    if not match:
        logging.warning(f"❌ Could not parse line: {line.strip()}")
        return None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            data['timestamp'], '%d/%b/%Y:%H:%M:%S %z'
        ).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        timestamp = data['timestamp']

    return {
        'ip_address': data['ip'],
        'timestamp': timestamp,
        'method': data['method'],
        'path': data['path'],
        'protocol': data['protocol'],
        'status_code': int(data['status_code']),
        'bytes_sent': int(data['response_size']) if data['response_size'] != '-' else 0,
        'referrer': data['referrer'],
        'user_agent': data['user_agent']
    }

def parse_log_file(filename):
    entries = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            entry = parse_log_line(line)
            if entry:
                entries.append(entry)
    logging.info(f"✅ Parsed {len(entries)} valid log entries.")
    return entries

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python log_parser.py <log_file_path>")
        sys.exit(1)

    log_file = sys.argv[1]
    results = parse_log_file(log_file)

    for entry in results[:5]:  # Preview first 5 entries
        print(entry)
