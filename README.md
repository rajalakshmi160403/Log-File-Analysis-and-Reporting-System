# LOG-FILE-ANALYSIS-AND-REPORTING-SYSTEM-
Log File Analysis and Reporting System. This Python tool parses Apache web server logs, stores them in MySQL, and generates actionable reports. 

## Features

- **Log Processing Engine**
  - Parses Apache Common/Combined Log Format
  - Regex-powered extraction of:
    - IP addresses
    - Timestamps
    - HTTP methods
    - URLs/paths
    - Status codes
    - Bytes transferred
    - User agents
  - Data normalization and type conversion

- **Database Integration**
  - Optimized MySQL schema
  - Batch inserts for high-volume data
  - Idempotent operations (handles duplicates)
  - Separate user agent table for efficient storage

- **Reporting & Analysis**
  - Top N IP addresses
  - Most requested URLs
  - Status code distributions
  - Hourly traffic patterns
  - Error analysis by date
  - OS/browser breakdowns

- **Performance Optimizations**
  - Memory-efficient processing
  - Configurable batch sizes
  - Error handling and logging
ort hourly_traffic

