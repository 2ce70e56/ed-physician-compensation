"""
Compensation calculation module for ED Physician Compensation System.
"""
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

class CompensationCalculator:
    """Handles calculation of physician compensation based on shifts and performance metrics."""
    
    def __init__(self, base_rate: float, shift_differentials: Dict[str, float],
                 wrvu_target: float, performance_threshold: float):
        """
        Initialize calculator with compensation parameters.
        
        Args:
            base_rate: Base hourly rate for regular shifts
            shift_differentials: Dictionary mapping shift types to differential rates
            wrvu_target: Target wRVUs per hour for productivity bonus
            performance_threshold: Required productivity percentage for performance bonus
        """
        self.base_rate = base_rate
        self.shift_differentials = shift_differentials
        self.wrvu_target = wrvu_target
        self.performance_threshold = performance_threshold
    
    def calculate_shift_pay(self, shift: pd.Series) -> Dict[str, float]:
        """
        Calculate compensation for a single shift.
        
        Args:
            shift: Series containing shift data
            
        Returns:
            Dictionary containing base pay and differential pay
        """
        start_time = pd.to_datetime(shift['start_time'])
        end_time = pd.to_datetime(shift['end_time'])
        duration = (end_time - start_time).total_seconds() / 3600
        
        # Calculate base pay
        base_pay = duration * self.base_rate
        
        # Apply shift differential if applicable
        differential_pay = 0.0
        shift_type = shift.get('shift_type')
        if shift_type in self.shift_differentials:
            differential_pay = duration * self.shift_differentials[shift_type]
        
        return {
            'shift_id': shift.get('shift_id'),
            'base_pay': base_pay,
            'differential_pay': differential_pay,
            'total_pay': base_pay + differential_pay
        }
    
    def calculate_productivity_metrics(self, shifts_df: pd.DataFrame,
                                    wrvu_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate productivity metrics based on wRVU data.
        
        Args:
            shifts_df: DataFrame containing shift data
            wrvu_data: DataFrame containing wRVU billing data
            
        Returns:
            DataFrame with productivity metrics per shift
        """
        # Merge shift and wRVU data
        merged_data = pd.merge(
            shifts_df,
            wrvu_data,
            on=['shift_id', 'physician_id'],
            how='left'
        )
        
        # Calculate hours and wRVUs per shift
        merged_data['shift_hours'] = (
            pd.to_datetime(merged_data['end_time']) - 
            pd.to_datetime(merged_data['start_time'])
        ).dt.total_seconds() / 3600
        
        merged_data['wrvus_per_hour'] = merged_data['wrvu'] / merged_data['shift_hours']
        merged_data['productivity_percentage'] = (
            merged_data['wrvus_per_hour'] / self.wrvu_target * 100
        )
        
        return merged_data
    
    def calculate_productivity_bonus(self, productivity_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate productivity bonuses based on wRVU metrics.
        
        Args:
            productivity_data: DataFrame containing productivity metrics
            
        Returns:
            DataFrame with bonus calculations
        """
        # Calculate bonus for shifts meeting productivity target
        bonus_data = productivity_data.copy()
        bonus_data['productivity_bonus'] = 0.0
        
        # Apply bonus for shifts exceeding target
        qualifying_shifts = bonus_data['productivity_percentage'] >= 100
        bonus_data.loc[qualifying_shifts, 'productivity_bonus'] = (
            bonus_data.loc[qualifying_shifts, 'total_pay'] * 0.10  # 10% bonus for meeting target
        )
        
        # Additional bonus for exceeding target
        high_performers = bonus_data['productivity_percentage'] >= 120
        bonus_data.loc[high_performers, 'productivity_bonus'] += (
            bonus_data.loc[high_performers, 'total_pay'] * 0.05  # Additional 5% for exceeding target
        )
        
        return bonus_data
    
    def calculate_performance_bonus(self, productivity_data: pd.DataFrame,
                                 evaluation_period: str = 'M') -> pd.DataFrame:
        """
        Calculate performance bonuses based on sustained productivity.
        
        Args:
            productivity_data: DataFrame containing productivity metrics
            evaluation_period: Period for grouping ('M' for month, 'Q' for quarter)
            
        Returns:
            DataFrame with performance bonus calculations
        """
        # Group data by physician and period
        grouped_data = productivity_data.groupby(
            ['physician_id', pd.Grouper(key='start_time', freq=evaluation_period)]
        ).agg({
            'productivity_percentage': 'mean',
            'total_pay': 'sum'
        }).reset_index()
        
        # Calculate performance bonus for qualifying periods
        grouped_data['performance_bonus'] = 0.0
        qualifying_periods = grouped_data['productivity_percentage'] >= self.performance_threshold
        
        grouped_data.loc[qualifying_periods, 'performance_bonus'] = (
            grouped_data.loc[qualifying_periods, 'total_pay'] * 0.15  # 15% bonus for sustained performance
        )
        
        return grouped_data
    
    def calculate_total_compensation(self, shifts_df: pd.DataFrame,
                                  wrvu_data: pd.DataFrame,
                                  evaluation_period: str = 'M') -> Dict[str, pd.DataFrame]:
        """
        Calculate complete compensation including all bonuses.
        
        Args:
            shifts_df: DataFrame containing shift data
            wrvu_data: DataFrame containing wRVU billing data
            evaluation_period: Period for performance evaluation
            
        Returns:
            Dictionary containing DataFrames for shift pay, productivity, and performance
        """
        # Calculate base shift compensation
        shift_pay = pd.DataFrame([
            self.calculate_shift_pay(shift) for _, shift in shifts_df.iterrows()
        ])
        
        # Calculate productivity metrics and bonus
        productivity_data = self.calculate_productivity_metrics(shifts_df, wrvu_data)
        productivity_data = pd.merge(productivity_data, shift_pay, on='shift_id')
        productivity_with_bonus = self.calculate_productivity_bonus(productivity_data)
        
        # Calculate performance bonus
        performance_data = self.calculate_performance_bonus(
            productivity_with_bonus, evaluation_period
        )
        
        return {
            'shift_compensation': shift_pay,
            'productivity_compensation': productivity_with_bonus,
            'performance_compensation': performance_data
        }
    
    def generate_compensation_report(self, compensation_data: Dict[str, pd.DataFrame],
                                  start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Generate a comprehensive compensation report for a specific period.
        
        Args:
            compensation_data: Dictionary containing compensation DataFrames
            start_date: Start date for the report period
            end_date: End date for the report period
            
        Returns:
            DataFrame containing summarized compensation data
        """
        # Filter data for the specified period
        period_mask = (
            pd.to_datetime(compensation_data['productivity_compensation']['start_time'])
            .between(start_date, end_date)
        )
        period_data = compensation_data['productivity_compensation'][period_mask]
        
        # Group by physician
        summary = period_data.groupby('physician_id').agg({
            'total_pay': 'sum',
            'productivity_bonus': 'sum',
            'shift_hours': 'sum',
            'wrvu': 'sum'
        }).reset_index()
        
        # Add performance bonus
        performance_mask = (
            pd.to_datetime(compensation_data['performance_compensation']['start_time'])
            .between(start_date, end_date)
        )
        performance_data = compensation_data['performance_compensation'][performance_mask]
        
        summary = pd.merge(
            summary,
            performance_data[['physician_id', 'performance_bonus']],
            on='physician_id',
            how='left'
        )
        
        # Calculate total compensation
        summary['total_compensation'] = (
            summary['total_pay'] +
            summary['productivity_bonus'] +
            summary['performance_bonus']
        )
        
        # Calculate averages
        summary['avg_wrvus_per_hour'] = summary['wrvu'] / summary['shift_hours']
        
        return summary
