# Project Architecture

## Overview
The system is designed to be modular and extensible, dividing responsibilities into distinct modules that handle data acquisition, validation, compensation calculation, and reporting.

## Modules

### 1. Database Module
- **Responsibilities:**
  - Establish a connection to SQL Server using `pyodbc` or `SQLAlchemy`.
  - Retrieve shift and orders data.
  - Insert scraped data into designated SQL tables.

### 2. Scraping Module
- **Responsibilities:**
  - Scrape shift data from amion.com.
  - Utilize either `requests`/`BeautifulSoup` for static pages or `Selenium` for dynamic content.
  - Transform and validate scraped data before insertion into SQL Server.

### 3. Validation Module
- **Responsibilities:**
  - Compare SQL Server shift data against scraped data.
  - Validate shift times against orders data.
  - Flag issues such as:
    - Shifts not starting on the hour.
    - Shifts outside permitted hours.
    - Overlapping shifts.
    - Unusually long shifts.
    - Early shifts not preceded by a valid shift.

### 4. Compensation Calculation Module
- **Responsibilities:**
  - Apply base pay and shift differential rules.
  - Map wRVU billing data to shifts.
  - Compute productivity and performance incentives based on predefined thresholds.

### 5. Parameters Management Module
- **Responsibilities:**
  - Store and manage dynamic compensation parameters.
  - Track parameter changes over time with versioning or effective date records.

### 6. Reporting & Logging Module
- **Responsibilities:**
  - Log all process steps, errors, and issues.
  - Generate reports in formats like CSV or Excel.
  - Provide summaries of shift issues and compensation breakdown.

## Data Flow
1. **Data Acquisition:**
   - **SQL Server:** Shift and orders data.
   - **amion.com:** Scraped shift data.
2. **Data Validation & Issue Detection:**
   - Compare and validate the various data sources.
   - Flag discrepancies.
3. **Compensation Calculation:**
   - Apply business rules to validated data.
   - Merge wRVU billing data.
4. **Reporting:**
   - Log outcomes and generate detailed reports.

## Technologies
- **Programming Language:** Python 3.x
- **Database:** SQL Server
- **Key Libraries:** `pyodbc` / `SQLAlchemy`, `pandas`, `requests`, `BeautifulSoup`, `Selenium`, `logging`