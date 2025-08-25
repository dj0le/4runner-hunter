#!/usr/bin/env python3
"""Test full run with all listings"""
import logging
import sys
sys.path.append('..')
from main import FourRunnerHunter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_full_run():
    print("Testing full 4Runner search...")
    print("This will fetch ALL listings and decode VINs - may take a few minutes")
    print("-" * 60)
    
    hunter = FourRunnerHunter()
    stats = hunter.search_4runners()
    
    print("\n" + "="*60)
    print("FINAL RESULTS:")
    print(f"Total listings checked: {stats['total_listings_found']}")
    print(f"New listings found: {stats['new_listings']}")
    print(f"Manual transmissions found: {stats['manual_listings_found']}")
    print(f"API calls made: {stats['api_calls_made']}")
    
    if stats['errors']:
        print(f"\nErrors encountered: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"  - {error}")
    
    # Get manual summary
    hunter.get_manual_summary()

if __name__ == "__main__":
    test_full_run()