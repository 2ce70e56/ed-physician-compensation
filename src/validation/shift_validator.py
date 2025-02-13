"""
Shift validation module for ED Physician Compensation System.
"""
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

class ShiftValidator:
    """Handles validation of shift data against various rules and sources."""
    
    def __init__(self, min_shift_hours: float = 4.0, max_shift_hours: float = 12.0,
                 early_start_threshold: time = time(5, 0)):
        """
        Initialize validator with configurable parameters.
        
        Args:
            min_shift_hours: Minimum allowed shift duration in hours
            max_shift_hours: Maximum allowed shift duration in hours
            early_start_threshold: Earliest allowed start time without preceding shift
        """
        self.min_shift_hours = min_shift_hours
        self.max_shift_hours = max_shift_hours
        self.early_start_threshold = early_start_threshold
    
    def validate_shift_times(self, shifts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate shift start/end times and durations.
        
        Args:
            shifts_df: DataFrame containing shift data
            
        Returns:
            DataFrame with validation issues flagged
        """
        issues = []
        
        for idx, shift in shifts_df.iterrows():
            start_time = pd.to_datetime(shift['start_time'])
            end_time = pd.to_datetime(shift['end_time'])
            
            # Check start times on the hour
            if start_time.minute != 0:
                issues.append({
                    'shift_id': shift.get('shift_id'),
                    'issue_type': 'non_hourly_start',
                    'description': f"Shift starts at {start_time.strftime('%H:%M')} instead of on the hour"
                })
            
            # Check shift duration
            duration = (end_time - start_time).total_seconds() / 3600
            if duration < self.min_shift_hours:
                issues.append({
                    'shift_id': shift.get('shift_id'),
                    'issue_type': 'short_shift',
                    'description': f"Shift duration ({duration:.1f} hours) is below minimum ({self.min_shift_hours} hours)"
                })
            elif duration > self.max_shift_hours:
                issues.append({
                    'shift_id': shift.get('shift_id'),
                    'issue_type': 'long_shift',
                    'description': f"Shift duration ({duration:.1f} hours) exceeds maximum ({self.max_shift_hours} hours)"
                })
        
        return pd.DataFrame(issues)
    
    def check_overlapping_shifts(self, shifts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify overlapping shifts for the same physician.
        
        Args:
            shifts_df: DataFrame containing shift data
            
        Returns:
            DataFrame with overlapping shifts flagged
        """
        issues = []
        
        # Sort shifts by physician and start time
        sorted_shifts = shifts_df.sort_values(['physician_id', 'start_time'])
        
        # Group by physician
        for physician_id, physician_shifts in sorted_shifts.groupby('physician_id'):
            shifts_list = physician_shifts.to_dict('records')
            
            for i in range(len(shifts_list) - 1):
                current_shift = shifts_list[i]
                next_shift = shifts_list[i + 1]
                
                current_end = pd.to_datetime(current_shift['end_time'])
                next_start = pd.to_datetime(next_shift['start_time'])
                
                if current_end > next_start:
                    issues.append({
                        'shift_id': next_shift.get('shift_id'),
                        'issue_type': 'overlapping_shift',
                        'description': (f"Shift overlaps with previous shift "
                                     f"(ends at {current_end.strftime('%Y-%m-%d %H:%M')})")
                    })
        
        return pd.DataFrame(issues)
    
    def validate_early_starts(self, shifts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Check for early morning shifts without preceding shifts.
        
        Args:
            shifts_df: DataFrame containing shift data
            
        Returns:
            DataFrame with early start issues flagged
        """
        issues = []
        
        # Sort shifts by physician and start time
        sorted_shifts = shifts_df.sort_values(['physician_id', 'start_time'])
        
        for physician_id, physician_shifts in sorted_shifts.groupby('physician_id'):
            shifts_list = physician_shifts.to_dict('records')
            
            for i in range(len(shifts_list)):
                current_shift = shifts_list[i]
                start_time = pd.to_datetime(current_shift['start_time'])
                
                # Check if shift starts before threshold
                if start_time.time() < self.early_start_threshold:
                    # Check if there's a preceding shift
                    if i == 0 or (pd.to_datetime(shifts_list[i-1]['end_time']).date() != start_time.date()):
                        issues.append({
                            'shift_id': current_shift.get('shift_id'),
                            'issue_type': 'early_start',
                            'description': (f"Shift starts at {start_time.strftime('%H:%M')} "
                                         f"without a preceding shift")
                        })
        
        return pd.DataFrame(issues)
    
    def validate_against_amion(self, actual_shifts: pd.DataFrame, 
                             scheduled_shifts: pd.DataFrame) -> pd.DataFrame:
        """
        Compare actual shifts against Amion schedule.
        
        Args:
            actual_shifts: DataFrame containing actual shift data
            scheduled_shifts: DataFrame containing Amion schedule data
            
        Returns:
            DataFrame with discrepancies flagged
        """
        issues = []
        
        # Merge actual and scheduled shifts
        merged_shifts = pd.merge(
            actual_shifts,
            scheduled_shifts,
            on=['date', 'physician_id'],
            suffixes=('_actual', '_scheduled'),
            how='outer'
        )
        
        for _, shift in merged_shifts.iterrows():
            # Check for missing actual shifts
            if pd.isna(shift.get('start_time_actual')):
                issues.append({
                    'shift_id': shift.get('shift_id_scheduled'),
                    'issue_type': 'missing_actual_shift',
                    'description': "Scheduled shift has no corresponding actual shift"
                })
                continue
            
            # Check for unscheduled shifts
            if pd.isna(shift.get('start_time_scheduled')):
                issues.append({
                    'shift_id': shift.get('shift_id_actual'),
                    'issue_type': 'unscheduled_shift',
                    'description': "Actual shift was not scheduled in Amion"
                })
                continue
            
            # Compare start and end times
            actual_start = pd.to_datetime(shift['start_time_actual'])
            actual_end = pd.to_datetime(shift['end_time_actual'])
            scheduled_start = pd.to_datetime(shift['start_time_scheduled'])
            scheduled_end = pd.to_datetime(shift['end_time_scheduled'])
            
            if actual_start != scheduled_start:
                issues.append({
                    'shift_id': shift.get('shift_id_actual'),
                    'issue_type': 'start_time_mismatch',
                    'description': (f"Actual start time ({actual_start.strftime('%H:%M')}) "
                                 f"differs from scheduled ({scheduled_start.strftime('%H:%M')})")
                })
            
            if actual_end != scheduled_end:
                issues.append({
                    'shift_id': shift.get('shift_id_actual'),
                    'issue_type': 'end_time_mismatch',
                    'description': (f"Actual end time ({actual_end.strftime('%H:%M')}) "
                                 f"differs from scheduled ({scheduled_end.strftime('%H:%M')})")
                })
        
        return pd.DataFrame(issues)
    
    def validate_all(self, actual_shifts: pd.DataFrame, 
                    scheduled_shifts: pd.DataFrame) -> pd.DataFrame:
        """
        Run all validation checks and combine results.
        
        Args:
            actual_shifts: DataFrame containing actual shift data
            scheduled_shifts: DataFrame containing Amion schedule data
            
        Returns:
            DataFrame containing all validation issues
        """
        all_issues = []
        
        # Run all validations
        time_issues = self.validate_shift_times(actual_shifts)
        overlap_issues = self.check_overlapping_shifts(actual_shifts)
        early_start_issues = self.validate_early_starts(actual_shifts)
        amion_issues = self.validate_against_amion(actual_shifts, scheduled_shifts)
        
        # Combine all issues
        for df in [time_issues, overlap_issues, early_start_issues, amion_issues]:
            if not df.empty:
                all_issues.append(df)
        
        if all_issues:
            return pd.concat(all_issues, ignore_index=True)
        return pd.DataFrame()