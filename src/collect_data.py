#!/usr/bin/env python3
"""
Data Collection Script for SME Dashboard
Run this script to collect fresh data from various sources
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collectors import DataCollector

def main():
    print("🚀 SME Dashboard Data Collection")
    print("=" * 40)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize collector
        collector = DataCollector()
        
        # Collect all data
        print("📥 Starting data collection process...")
        collector.collect_all_data()
        
        print()
        print("✅ Data collection completed successfully!")
        print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)