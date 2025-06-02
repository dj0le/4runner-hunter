#!/usr/bin/env python3
"""View manual 4Runner findings from the database"""
import sqlite3
from datetime import datetime
import sys
sys.path.append('..')
from config import DATABASE_PATH

def view_manual_4runners():
    """Display all manual 4Runners found"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all manual 4Runners
    cursor.execute("""
        SELECT * FROM listings 
        WHERE is_manual = 1 
        ORDER BY year DESC, price ASC
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("No manual 4Runners found yet!")
        return
    
    print(f"\n{'='*80}")
    print(f"MANUAL 4RUNNERS FOUND: {len(results)}")
    print(f"{'='*80}\n")
    
    for row in results:
        print(f"Year: {row['year']} | Price: ${row['price']:,} | Mileage: {row['mileage']:,} mi")
        print(f"Location: {row['city']}, {row['state']} | Dealer: {row['dealer_name']}")
        print(f"Transmission: {row['transmission_type']} | Engine: {row['engine_info']}")
        print(f"Trim: {row['trim']} | Drivetrain: {row['drivetrain']}")
        print(f"VIN: {row['vin']}")
        print(f"First seen: {row['first_seen']}")
        print(f"Last seen: {row['last_seen']}")
        print("-" * 80)
    
    # Show summary statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price) as avg_price,
            MIN(mileage) as min_mileage,
            MAX(mileage) as max_mileage,
            AVG(mileage) as avg_mileage
        FROM listings 
        WHERE is_manual = 1
    """)
    
    stats = cursor.fetchone()
    print(f"\nSUMMARY STATISTICS:")
    print(f"Total manual 4Runners: {stats['total']}")
    print(f"Price range: ${stats['min_price']:,} - ${stats['max_price']:,} (avg: ${stats['avg_price']:,.0f})")
    print(f"Mileage range: {stats['min_mileage']:,} - {stats['max_mileage']:,} mi (avg: {stats['avg_mileage']:,.0f} mi)")
    
    # Show by year
    cursor.execute("""
        SELECT year, COUNT(*) as count 
        FROM listings 
        WHERE is_manual = 1 
        GROUP BY year 
        ORDER BY year
    """)
    
    print(f"\nBY YEAR:")
    for row in cursor.fetchall():
        print(f"  {row['year']}: {row['count']} vehicles")
    
    conn.close()

def view_all_listings():
    """View all listings (manual and automatic)"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_manual = 1 THEN 1 ELSE 0 END) as manual_count
        FROM listings
    """)
    
    stats = cursor.fetchone()
    print(f"\nTOTAL DATABASE STATS:")
    print(f"Total 4Runners tracked: {stats[0]}")
    print(f"Manual transmissions: {stats[1]}")
    print(f"Automatic transmissions: {stats[0] - stats[1]}")
    print(f"Manual percentage: {(stats[1]/stats[0]*100):.1f}%")
    
    conn.close()

def export_to_csv():
    """Export manual 4Runners to CSV file"""
    import csv
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM listings 
        WHERE is_manual = 1 
        ORDER BY year DESC, price ASC
    """)
    
    results = cursor.fetchall()
    
    if results:
        filename = f"manual_4runners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['year', 'price', 'mileage', 'city', 'state', 'dealer_name', 
                         'transmission_type', 'engine_info', 'trim', 'drivetrain', 'vin', 
                         'first_seen', 'last_seen']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in results:
                writer.writerow({field: row[field] for field in fieldnames})
        
        print(f"\nExported {len(results)} manual 4Runners to {filename}")
    
    conn.close()

if __name__ == "__main__":
    print("4RUNNER MANUAL TRANSMISSION DATABASE VIEWER")
    print("=" * 80)
    
    view_manual_4runners()
    view_all_listings()
    
    # Ask if user wants to export
    response = input("\nExport results to CSV? (y/n): ")
    if response.lower() == 'y':
        export_to_csv()