import argparse
import os
import configparser
from mysql_handler import MySQLHandler
from log_parser import parse_log_line

# Load DB config
config = configparser.ConfigParser()
config.read('config.ini')

DB_CONFIG = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database']
}

def process_logs(file_path, batch_size=1000):
    print(f"📁 Processing log file: {file_path}")
    db = MySQLHandler(**DB_CONFIG)
    db.create_tables()

    total = 0
    batch = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = parse_log_line(line)
                if entry:
                    batch.append(entry)
                    if len(batch) >= batch_size:
                        db.insert_batch_log_entries(batch)
                        total += len(batch)
                        print(f"[INFO] - Processed {total} lines.")
                        batch = []

        if batch:
            db.insert_batch_log_entries(batch)
            total += len(batch)
            print(f"[INFO] - Processed {total} lines.")

        print(f"[✅ DONE] Finished processing. Total parsed and inserted entries: {total}")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

def generate_report(report_type, limit=None, date=None):
    db = MySQLHandler(**DB_CONFIG)
    try:
        if report_type == "top_n_ips":
            results = db.get_top_n_ips(limit or 5)
            print(f"\n{'IP Address':<20}{'Request Count':>15}")
            print("-" * 35)
            for ip, count in results:
                print(f"{ip:<20}{count:>15}")

        elif report_type == "top_n_pages":
            results = db.cursor.execute('''
                SELECT path, COUNT(*) as count
                FROM log_entries
                GROUP BY path
                ORDER BY count DESC
                LIMIT %s
            ''', (limit or 5,))
            results = db.cursor.fetchall()
            print(f"\n{'Page Path':<60}{'Request Count':>15}")
            print("-" * 75)
            for path, count in results:
                print(f"{path[:58]:<60}{count:>15}")

        elif report_type == "status_code_distribution":
            results = db.get_status_code_distribution()
            print(f"\n{'Status Code':<15}{'Count':<10}{'Percentage':<10}")
            print("-" * 35)
            for code, count, percent in results:
                print(f"{code:<15}{count:<10}{percent:<10}")

        elif report_type == "hourly_traffic":
            results = db.get_hourly_traffic()
            print(f"\n{'Hour':<10}{'Request Count':>15}")
            print("-" * 25)
            for hour, count in results:
                print(f"{hour:02d}:00{'':<5}{count:>10}")

        elif report_type == "error_logs_by_date":
            if not date:
                print("❌ Please provide a date using --date YYYY-MM-DD")
            else:
                results = db.get_error_logs_by_date(date)
                print(f"\n{'IP Address':<15} {'Timestamp':<20} {'Method':<7} {'Path':<30} {'Status':<6}")
                print("-" * 90)
                for ip, ts, method, path, status in results:
                    print(f"{ip:<15} {str(ts)[:19]:<20} {method:<7} {path[:28]:<30} {status:<6}")

        elif report_type == "traffic_by_os":
            results = db.get_traffic_by_os()
            print(f"\n{'Operating System':<30}{'Request Count':>15}")
            print("-" * 45)
            for os_name, count in results:
                print(f"{os_name:<30}{count:>15}")

        print()  # Add empty line after report

    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="🧪 Log Analyzer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Process logs
    process_parser = subparsers.add_parser("process_logs", help="Process a log file")
    process_parser.add_argument("filename", help="Path to the log file")
    process_parser.add_argument("--batch_size", type=int, default=1000, 
                              help="Batch size for DB insert")

    # Reports
    report_parser = subparsers.add_parser("generate_report", help="Generate reports")
    report_parser.add_argument("report_type", choices=[
        "top_n_ips",
        "top_n_pages",
        "status_code_distribution",
        "hourly_traffic",
        "error_logs_by_date",
        "traffic_by_os"
    ], help="Type of report to generate")
    report_parser.add_argument("--limit", type=int, 
                             help="Limit for top_n reports (default: 5)")
    report_parser.add_argument("--date", 
                             help="Date for error_logs_by_date (format: YYYY-MM-DD)")

    args = parser.parse_args()

    if args.command == "process_logs":
        process_logs(args.filename, args.batch_size)
    elif args.command == "generate_report":
        generate_report(args.report_type, limit=args.limit, date=args.date)

if __name__ == "__main__":
    main()