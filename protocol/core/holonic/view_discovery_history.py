#!/usr/bin/env python3

import os
import sys

# Add the parent directory to the Python path so we can import the db module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Go up one level
sys.path.append(parent_dir)

# Now import the database connection
from db.connection import DatabaseManager

def view_holder_discovery_history():
    db = DatabaseManager(schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'))
    query = """
    SELECT 
        discovery_date, 
        account_id, 
        discovery_source, 
        initial_balance, 
        is_new, 
        added_to_tracking
    FROM holder_discovery_history 
    ORDER BY discovery_date DESC
    LIMIT 50;
    """
    
    results = db.execute_query(query, fetch_all=True)
    
    if not results:
        print("No records found in holder_discovery_history table.")
        return
    
    # Print the results in a simple format if tabulate is not available
    print("\nHOLDER DISCOVERY HISTORY")
    print("="*80)
    
    # Print headers
    headers = list(results[0].keys())
    header_str = "  ".join(f"{h:<20}" for h in headers)
    print(header_str)
    print("-"*80)
    
    # Print data rows
    for row in results:
        row_str = "  ".join(f"{str(row[h]):<20}" for h in headers)
        print(row_str)
    
    print("="*80)
    print(f"Total records shown: {len(results)}")
    
if __name__ == "__main__":
    view_holder_discovery_history()
