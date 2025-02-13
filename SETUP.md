# Project Setup

## Prerequisites
- **Python 3.x** installed
- **SQL Server** instance with proper access credentials
- **Python Libraries:**
  - `pyodbc` or `SQLAlchemy` (for database connections)
  - `pandas` (for data handling)
  - `requests` and `beautifulsoup4` or `Selenium` (for web scraping)
  - `logging` (for error tracking)
  - `schedule` (optional, for task scheduling)

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
DB_SERVER=your_server_name
DB_NAME=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password

AMION_USERNAME=your_amion_username
AMION_PASSWORD=your_amion_password
```

### 5. Initialize Database
```bash
python scripts/init_db.py
```

### 6. Verify Installation
```bash
python scripts/test_connection.py
```

## Development Setup
1. Install additional development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

## Running Tests
```bash
python -m pytest tests/
```

## Troubleshooting
Refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for common issues and solutions.