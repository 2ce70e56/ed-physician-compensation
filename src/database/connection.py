"""
Database connection module for ED Physician Compensation System.
"""
import os
from typing import Any, Dict

import pyodbc
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """Handles database connections and operations."""
    
    def __init__(self):
        """Initialize database connection parameters."""
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_NAME')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.conn = None
        self.cursor = None
    
    def connect(self) -> None:
        """Establish database connection."""
        connection_string = (
            f'DRIVER={{SQL Server}};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password}'
        )
        
        try:
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
        except pyodbc.Error as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> pyodbc.Cursor:
        """Execute SQL query with optional parameters."""
        try:
            if params:
                return self.cursor.execute(query, params)
            return self.cursor.execute(query)
        except pyodbc.Error as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()