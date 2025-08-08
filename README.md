# Log Analyzer CLI

A Python tool for parsing Apache combined logs, storing them in MySQL, and generating insightful reports.

## 🚀 Features
- Parse Apache combined/access logs
- Store in MySQL with proper schema
- Batch processing for large files
- Generate reports: top IPs/pages, status codes, hourly traffic, OS breakdown

## ⚙️ Setup
1. Clone repo: `git clone https://github.com/yourusername/log-analyzer.git`
2. Create virtualenv: `python -m venv venv`
3. Install deps: `pip install -r requirements.txt`
4. Configure MySQL in `config.ini`:
   ```ini
   [mysql]
   host = localhost
   user = root
   password = 12345
   database = weblogs_db

## Usage
Process logs:
python main.py process_logs access.log [--batch_size 10000]

## Generate reports:
# Top 10 IPs
python main.py generate_report top_n_ips --limit 10

# Status codes
python main.py generate_report status_code_distribution

# Hourly traffic
python main.py generate_report hourly_traffic
