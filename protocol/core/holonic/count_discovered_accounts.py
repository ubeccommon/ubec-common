#!/usr/bin/env python3

import os
import sys

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from db.connection import DatabaseManager

def count_discovered_accounts():
    try:
        db = DatabaseManager(schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'))
        
        # Get total count
        query = "SELECT COUNT(*) as total FROM holder_discovery_history"
        result = db.execute_query(query, fetch_one=True)
        total_count = result['total'] if result else 0
        
        # Get count of new discoveries
        query_new = "SELECT COUNT(*) as new_count FROM holder_discovery_history WHERE is_new = TRUE"
        result_new = db.execute_query(query_new, fetch_one=True)
        new_count = result_new['new_count'] if result_new else 0
        
        # Get count by source
        query_by_source = """
        SELECT discovery_source, COUNT(*) as count 
        FROM holder_discovery_history 
        GROUP BY discovery_source 
        ORDER BY count DESC
        """
        results_by_source = db.execute_query(query_by_source, fetch_all=True)
        
        # Display results
        print("\nUBEC ACCOUNT DISCOVERY STATISTICS")
        print("="*50)
        print(f"Total discovered accounts: {total_count}")
        print(f"New accounts: {new_count}")
        print(f"Previously known accounts: {total_count - new_count}")
        
        print("\nDiscovery Sources:")
        for row in results_by_source:
            print(f"  {row['discovery_source']}: {row['count']} accounts")
        
        # Get accounts added to tracking
        query_tracked = "SELECT COUNT(*) as count FROM holder_discovery_history WHERE added_to_tracking = TRUE"
        result_tracked = db.execute_query(query_tracked, fetch_one=True)
        tracked_count = result_tracked['count'] if result_tracked else 0
        
        print(f"\nAccounts added to tracking: {tracked_count}")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    count_discovered_accounts()
