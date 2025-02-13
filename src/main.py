"""
Main entry point for ED Physician Compensation System.
"""
import logging
import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv

from database.connection import DatabaseConnection
from scraper.amion_scraper import AmionScraper
from validation.shift_validator import ShiftValidator
from compensation.calculator import CompensationCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ed_compensation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_compensation_parameters():
    """Load compensation parameters from configuration."""
    # TODO: Load from database or config file
    return {
        'base_rate': 200.0,  # Base hourly rate
        'shift_differentials': {
            'night': 50.0,    # Additional per hour for night shifts
            'weekend': 25.0,  # Additional per hour for weekend shifts
            'holiday': 75.0   # Additional per hour for holiday shifts
        },
        'wrvu_target': 2.5,   # Target wRVUs per hour
        'performance_threshold': 90.0  # Minimum productivity percentage for performance bonus
    }

def process_shift_data(start_date: datetime, end_date: datetime):
    """
    Process shift data for the specified date range.
    
    Args:
        start_date: Start date for processing
        end_date: End date for processing
    """
    try:
        logger.info(f"Starting shift data processing for {start_date} to {end_date}")
        
        # Initialize components
        db = DatabaseConnection()
        scraper = AmionScraper()
        validator = ShiftValidator()
        comp_params = load_compensation_parameters()
        calculator = CompensationCalculator(**comp_params)
        
        # Scrape Amion schedule
        logger.info("Fetching Amion schedule data...")
        scheduled_shifts = scraper.get_shifts(start_date, end_date)
        scheduled_shifts_df = scraper.export_to_dataframe(scheduled_shifts)
        
        with db:
            # Store scraped data
            logger.info("Storing scraped schedule data...")
            # TODO: Implement database storage
            
            # Retrieve actual shift data
            logger.info("Retrieving actual shift data...")
            actual_shifts_query = """
                SELECT shift_id, physician_id, start_time, end_time, shift_type
                FROM shifts
                WHERE start_time BETWEEN ? AND ?
            """
            actual_shifts = db.execute_query(
                actual_shifts_query, 
                {'start_date': start_date, 'end_date': end_date}
            )
            actual_shifts_df = pd.DataFrame(actual_shifts.fetchall())
            
            # Retrieve wRVU data
            logger.info("Retrieving wRVU billing data...")
            wrvu_query = """
                SELECT shift_id, physician_id, SUM(wrvu) as wrvu
                FROM billing_data
                WHERE service_date BETWEEN ? AND ?
                GROUP BY shift_id, physician_id
            """
            wrvu_data = db.execute_query(
                wrvu_query,
                {'start_date': start_date, 'end_date': end_date}
            )
            wrvu_df = pd.DataFrame(wrvu_data.fetchall())
        
        # Validate shifts
        logger.info("Validating shift data...")
        validation_issues = validator.validate_all(actual_shifts_df, scheduled_shifts_df)
        
        if not validation_issues.empty:
            logger.warning(f"Found {len(validation_issues)} validation issues")
            # TODO: Store validation issues in database
        
        # Calculate compensation
        logger.info("Calculating compensation...")
        compensation_data = calculator.calculate_total_compensation(
            actual_shifts_df,
            wrvu_df,
            evaluation_period='M'
        )
        
        # Generate report
        logger.info("Generating compensation report...")
        report = calculator.generate_compensation_report(
            compensation_data,
            start_date,
            end_date
        )
        
        # TODO: Store compensation results
        logger.info("Processing completed successfully")
        return report
        
    except Exception as e:
        logger.error(f"Error processing shift data: {str(e)}", exc_info=True)
        raise

def main():
    """Main execution function."""
    load_dotenv()
    
    # Process previous month by default
    today = datetime.now()
    start_date = datetime(today.year, today.month, 1) - timedelta(days=1)
    start_date = datetime(start_date.year, start_date.month, 1)
    end_date = datetime(today.year, today.month, 1) - timedelta(days=1)
    
    try:
        report = process_shift_data(start_date, end_date)
        # TODO: Save report to file or database
        logger.info("Compensation processing completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()