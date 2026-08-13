#!/usr/bin/env python3
"""
View latest UBEC transactions script

This script connects to the UBEC database and displays the latest 20 UBEC transactions.
Run from the project root directory to ensure correct module imports.
"""

import os
import sys
import datetime
from decimal import Decimal

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import database connection
try:
    from db.connection import DatabaseManager
    print(f"Successfully imported DatabaseManager")
except ImportError as e:
    print(f"Error importing DatabaseManager: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def format_date(timestamp):
    """Format timestamp as a readable date string"""
    if isinstance(timestamp, str):
        # Try to parse ISO format
        try:
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return timestamp
    elif isinstance(timestamp, datetime.datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(timestamp)

def format_amount(amount):
    """Format decimal amount with commas"""
    if amount is None:
        return "N/A"
    try:
        if isinstance(amount, str):
            amount = Decimal(amount)
        return f"{float(amount):,.7f}"
    except:
        return str(amount)

def truncate_address(address, length=10):
    """Truncate Stellar address for display"""
    if not address:
        return "N/A"
    if len(address) <= length * 2:
        return address
    return f"{address[:length]}...{address[-length:]}"

def view_latest_transactions(limit=20, account_filter=None):
    """
    View the latest UBEC transactions
    
    Args:
        limit: Number of transactions to show
        account_filter: Optional account address to filter transactions
    """
    try:
        # Connect to database
        db = DatabaseManager(schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'))
        
        # Build query
        query = """
        SELECT 
            operation_id,
            transaction_id,
            created_at,
            operation_type,
            source_account,
            destination_account,
            asset_code,
            asset_issuer,
            amount
        FROM 
            transaction_operations
        WHERE 
            asset_code = 'UBEC'
        """
        
        # Add account filter if provided
        params = []
        if account_filter:
            query += " AND (source_account = %s OR destination_account = %s)"
            params.extend([account_filter, account_filter])
        
        # Add ordering and limit
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        # Execute query
        results = db.execute_query(query, params, fetch_all=True)
        
        if not results:
            print("No UBEC transactions found.")
            return
        
        # Print the results
        print("\nLATEST UBEC TRANSACTIONS")
        print("="*100)
        
        # Print each transaction in a readable format
        for i, tx in enumerate(results, 1):
            print(f"{i}. Transaction: {tx['operation_id']}")
            print(f"   Hash: {tx['transaction_id']}")
            print(f"   Date: {format_date(tx['created_at'])}")
            print(f"   Type: {tx['operation_type']}")
            print(f"   From: {truncate_address(tx['source_account'])}")
            print(f"   To:   {truncate_address(tx['destination_account'])}")
            print(f"   Amount: {format_amount(tx['amount'])} {tx['asset_code']}")
            print("-"*100)
        
        print(f"Total transactions shown: {len(results)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to parse arguments and execute"""
    import argparse
    
    parser = argparse.ArgumentParser(description="View latest UBEC transactions")
    parser.add_argument('--limit', type=int, default=20, 
                        help='Number of transactions to show (default: 20)')
    parser.add_argument('--account', type=str, 
                        help='Filter transactions by account address')
    
    args = parser.parse_args()
    
    view_latest_transactions(limit=args.limit, account_filter=args.account)

if __name__ == "__main__":
    main()
