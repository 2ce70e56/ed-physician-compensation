# ED Physician Compensation Management System

## Overview
This project is a Python-based system designed to manage and calculate ED physician compensation. The solution integrates data from SQL Server, scrapes shift data from amion.com, validates shifts against orders, and applies business rules for calculating base pay, shift differentials, and incentive-based compensation.

## Features
- **Database Integration:** Retrieve shift and orders data from SQL Server.
- **Web Scraping:** Extract shift details from amion.com.
- **Data Validation:** Compare SQL data with scraped data and orders to identify discrepancies.
- **Issue Detection:** Identify anomalies like non-standard start times, off-hour shifts, overlapping shifts, etc.
- **Compensation Calculations:** Apply shift differentials, wRVU billing integration, productivity incentives, and performance incentives.
- **Reporting:** Log errors and generate reports for review.

## Project Structure
- **Database Module:** Connects and queries SQL Server.
- **Scraping Module:** Handles amion.com scraping.
- **Validation Module:** Validates and flags discrepancies.
- **Compensation Module:** Applies business rules to calculate compensation.
- **Parameters Module:** Manages dynamic compensation parameters.
- **Reporting Module:** Generates logs and reports.

## Getting Started
Refer to the [SETUP.md](SETUP.md) file for environment setup and installation instructions.

## Documentation
For a detailed look at the project architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Tasks
For a breakdown of project tasks and milestones, see [TASKS.md](TASKS.md).