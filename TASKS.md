# Project Tasks

## Phase 1: Database Connection and Data Retrieval
- [ ] Set up SQL Server connection using `pyodbc` or `SQLAlchemy`.
- [ ] Write scripts to retrieve shift and orders data.
- [ ] Load data into pandas DataFrames for initial testing.
- [ ] Implement error handling and logging for database operations.

## Phase 2: External Data Acquisition (amion.com Scraping)
- [ ] Decide on the scraping method: `requests/BeautifulSoup` or `Selenium`.
- [ ] Develop a script to log in (if required) and navigate to the amion.com calendar.
- [ ] Extract shift details (dates, times, physician IDs).
- [ ] Validate and insert the scraped data into a designated SQL table.
- [ ] Implement error handling for potential webpage structure changes.

## Phase 3: Data Validation
- [ ] Create functions to compare SQL shift data with scraped data.
- [ ] Cross-reference shifts with orders data.
- [ ] Identify and log discrepancies.
- [ ] Test validation functions using sample data sets.

## Phase 4: Issue Detection and Flagging
- [ ] Develop functions to detect:
    - Shifts not starting on the hour.
    - Shifts outside allowed working hours.
    - Shifts with unusually high durations.
    - Overlapping shifts.
    - Shifts starting before 5am without a valid preceding shift.
- [ ] Log detected issues in a report or CSV file for review.

## Phase 5: Compensation Calculations
- [ ] Define business rules for base compensation and shift differentials.
- [ ] Develop functions to apply these rules based on validated shift data.
- [ ] Retrieve and map wRVU billing data to corresponding shifts.
- [ ] Calculate productivity incentives based on wRVU thresholds.
- [ ] Compute performance incentives for qualifying shifts.
- [ ] Test compensation calculations under various scenarios.

## Phase 6: Integration and Reporting
- [ ] Integrate all modules into a cohesive system.
- [ ] Develop a reporting module to generate logs and summary reports.
- [ ] Implement comprehensive error handling and logging.
- [ ] Conduct end-to-end testing with sample data.
- [ ] Schedule periodic runs using a task scheduler (e.g., `cron` or the `schedule` library).

## Phase 7: Documentation and Deployment
- [ ] Finalize project documentation.
- [ ] Prepare deployment scripts and configuration files.
- [ ] Set up monitoring and logging for the production environment.
- [ ] Perform a final review and deploy the project.