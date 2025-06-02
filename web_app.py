#!/usr/bin/env python3
"""Flask web app for viewing manual 4Runner listings (1984-2002)"""
from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import logging
from datetime import datetime
from config import DATABASE_PATH

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_price(price):
    """Format price for display"""
    if not price or price == 0:
        return "Price not available"
    return f"${price:,}"

def format_mileage(mileage):
    """Format mileage for display"""
    if not mileage or mileage == 0:
        return "Mileage not available"
    return f"{mileage:,} miles"

def calculate_days_on_market(first_seen_str):
    """Calculate days on market from first_seen timestamp"""
    try:
        first_seen = datetime.fromisoformat(first_seen_str.replace('Z', '+00:00'))
        return (datetime.now() - first_seen).days
    except (ValueError, AttributeError):
        return 0

def format_engine_display(engine_info):
    """Format engine info for display, prioritizing engine code"""
    if not engine_info:
        return "Unknown"
    
    # Check for known engine codes at the start
    engine_codes = {
        '5VZ-FE': '5VZ-FE (3.4L V6)',
        '3RZ-FE': '3RZ-FE (2.7L 4cyl)',
        '3VZ-E': '3VZ-E (3.0L V6)',
        '22R-E': '22R-E (2.4L 4cyl)'
    }
    
    for code, display in engine_codes.items():
        if engine_info.startswith(code):
            return display
    
    # Fallback to original if no code found
    return engine_info

def _construct_auto_dev_url(row, listing_data):
    """Construct a proper auto.dev URL"""
    # Try to use the listing ID to create a more specific URL
    listing_id = listing_data.get('id', '')
    vin = row['vin']
    year = row['year']
    
    # Auto.dev URLs typically follow this pattern
    if listing_id:
        return f"https://auto.dev/listings/{listing_id}"
    elif vin:
        # Fallback to VIN-based URL
        return f"https://auto.dev/search?vin={vin}"
    else:
        # Last resort - search by year
        return f"https://auto.dev/search?make=Toyota&model=4Runner&year={year}"

@app.route('/')
def index():
    """Main page showing all target 4Runners (1984-2002)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get filter parameters
    filter_type = request.args.get('filter', 'all')  # all, manual, first_gen, auto, watched, gen1, gen2, gen3, under200k, 3.4l, within500
    sort_by = request.args.get('sort', 'price')      # price, year, mileage, days, distance

    # Build query based on filter
    if filter_type == 'manual':
        where_clause = "WHERE is_manual = 1 AND (is_first_gen IS NULL OR is_first_gen = 0)"
    elif filter_type == 'first_gen':
        where_clause = "WHERE is_first_gen = 1"
    elif filter_type == 'auto':
        where_clause = "WHERE is_manual = 0"
    elif filter_type == 'watched':
        where_clause = "WHERE is_watched = 1"
    elif filter_type == 'gen1':
        where_clause = "WHERE year >= 1984 AND year <= 1989"
    elif filter_type == 'gen2':
        where_clause = "WHERE year >= 1990 AND year <= 1995"
    elif filter_type == 'gen3':
        where_clause = "WHERE year >= 1996 AND year <= 2002"
    elif filter_type == 'under200k':
        where_clause = "WHERE mileage > 0 AND mileage < 200000"
    elif filter_type == '3.4l':
        where_clause = "WHERE engine_info LIKE '5VZ-FE%' OR engine_info LIKE '%3.4%'"
    elif filter_type == 'within500':
        where_clause = "WHERE distance_from_origin <= 500"
    else:  # all
        where_clause = "WHERE 1=1"

    # Build order clause
    if sort_by == 'year':
        order_clause = "ORDER BY year ASC"
    elif sort_by == 'mileage':
        order_clause = "ORDER BY mileage ASC"
    elif sort_by == 'days':
        order_clause = "ORDER BY first_seen DESC"
    elif sort_by == 'distance':
        order_clause = "ORDER BY distance_from_origin ASC"
    else:  # price
        order_clause = "ORDER BY price ASC"

    # Get listings
    query = f"""
        SELECT * FROM listings
        {where_clause}
        {order_clause}
    """
    cursor.execute(query)

    listings = []
    for row in cursor.fetchall():
        try:
            # Parse the raw listing data
            listing_data = {}
            if row['raw_listing_data']:
                listing_data = json.loads(row['raw_listing_data'])
        except (json.JSONDecodeError, TypeError):
            listing_data = {}

        # Determine vehicle category (with safe column access)
        category = "Unknown"
        try:
            is_first_gen = row['is_first_gen'] if 'is_first_gen' in row.keys() else False
            is_manual = row['is_manual'] if 'is_manual' in row.keys() else False

            if is_first_gen:
                category = "1st Gen (1984-1989)"
            elif is_manual:
                category = "Manual Transmission"
            else:
                category = "Automatic"
        except (KeyError, IndexError):
            # Fallback if columns don't exist
            category = "Unknown"
        
        # Generate dealer search URL
        dealer_name = row['dealer_name'] or ''
        city = row['city'] or ''
        state = row['state'] or ''
        dealer_search_url = None
        if dealer_name and (city or state):
            location = f"{city}, {state}" if city else state
            dealer_search_url = f"https://www.google.com/search?q={dealer_name}, {location}"

        # Build the listing object
        listing = {
            'vin': row['vin'],
            'year': row['year'],
            'price': row['price'],
            'price_formatted': format_price(row['price']),
            'mileage': row['mileage'],
            'mileage_formatted': format_mileage(row['mileage']),
            'city': row['city'] or 'Unknown',
            'state': row['state'] or 'Unknown',
            'location': f"{row['city'] or 'Unknown'}, {row['state'] or 'Unknown'}",
            'dealer_name': row['dealer_name'] or 'Unknown Dealer',
            'transmission_type': row['transmission_type'] or 'Unknown',
            'engine_info': format_engine_display(row['engine_info']),
            'engine_info_raw': row['engine_info'] or 'Unknown',
            'trim': row['trim'] or 'Unknown',
            'drivetrain': row['drivetrain'] or 'Unknown',
            'first_seen': row['first_seen'],
            'last_seen': row['last_seen'],
            'category': category,
            'is_manual': is_manual,
            'is_first_gen': is_first_gen,
            'manual_source': row['manual_source'] if 'manual_source' in row.keys() else 'Unknown',
            'vin_pattern_confidence': row['vin_pattern_confidence'] if 'vin_pattern_confidence' in row.keys() else 0,
            'model_code': row['model_code'] if 'model_code' in row.keys() else 'Unknown',

            # URLs - Construct proper auto.dev URL
            'auto_dev_url': _construct_auto_dev_url(row, listing_data),
            'dealer_url': listing_data.get('clickoffUrl', ''),
            'dealer_search_url': dealer_search_url,

            # Photos
            'primary_photo': listing_data.get('primaryPhotoUrl', ''),
            'all_photos': listing_data.get('photoUrls', []),
            'thumbnail_url': listing_data.get('thumbnailUrl', ''),

            # Additional info
            'dealer_id': listing_data.get('trackingParams', {}).get('remoteDealerId', ''),
            'listing_id': listing_data.get('id', ''),
            'days_on_market': calculate_days_on_market(row['first_seen']) if row['first_seen'] else 0,
            
            # Colors
            'exterior_color': row['exterior_color'] if 'exterior_color' in row.keys() else listing_data.get('displayColor', 'Unknown'),
            'interior_color': row['interior_color'] if 'interior_color' in row.keys() else listing_data.get('interiorColor', 'Unknown'),
            
            # User tracking
            'is_seen': row['is_seen'] if 'is_seen' in row.keys() else False,
            'is_watched': row['is_watched'] if 'is_watched' in row.keys() else False,
            
            # Additional data
            'distance_from_origin': row['distance_from_origin'] if 'distance_from_origin' in row.keys() else None,
            'created_at': row['created_at'] if 'created_at' in row.keys() else None,
            'color_options': row['color_options'] if 'color_options' in row.keys() else None
        }

        # Fix dealer URL if needed
        if listing['dealer_url'] and not listing['dealer_url'].startswith('http'):
            listing['dealer_url'] = f"https://{listing['dealer_url']}"

        # Fix photo URLs if needed
        if listing['primary_photo'] and not listing['primary_photo'].startswith('http'):
            listing['primary_photo'] = f"https:{listing['primary_photo']}"

        listings.append(listing)

    # Get summary statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total_count,
            COUNT(CASE WHEN is_manual = 1 AND (is_first_gen IS NULL OR is_first_gen = 0) THEN 1 END) as manual_count,
            COUNT(CASE WHEN is_first_gen = 1 THEN 1 END) as first_gen_count,
            COUNT(CASE WHEN year >= 1990 AND year <= 1995 THEN 1 END) as second_gen_count,
            COUNT(CASE WHEN year >= 1996 AND year <= 2002 THEN 1 END) as third_gen_count,
            COUNT(CASE WHEN is_manual = 0 THEN 1 END) as auto_count,
            MIN(CASE WHEN price > 0 THEN price END) as min_price,
            MAX(price) as max_price,
            AVG(CASE WHEN price > 0 THEN price END) as avg_price,
            MIN(CASE WHEN mileage > 0 THEN mileage END) as min_mileage,
            MAX(mileage) as max_mileage,
            AVG(CASE WHEN mileage > 0 THEN mileage END) as avg_mileage
        FROM listings
    """)
    stats_row = cursor.fetchone()

    stats = {
        'total_count': stats_row['total_count'] or 0,
        'manual_count': stats_row['manual_count'] or 0,
        'first_gen_count': stats_row['first_gen_count'] or 0,
        'second_gen_count': stats_row['second_gen_count'] or 0,
        'third_gen_count': stats_row['third_gen_count'] or 0,
        'auto_count': stats_row['auto_count'] or 0,
        'min_price': format_price(stats_row['min_price']),
        'max_price': format_price(stats_row['max_price']),
        'avg_price': format_price(int(stats_row['avg_price']) if stats_row['avg_price'] else 0),
        'min_mileage': format_mileage(stats_row['min_mileage']),
        'max_mileage': format_mileage(stats_row['max_mileage']),
        'avg_mileage': format_mileage(int(stats_row['avg_mileage']) if stats_row['avg_mileage'] else 0),
    }

    conn.close()

    return render_template('index.html',
                         listings=listings,
                         stats=stats,
                         current_filter=filter_type,
                         current_sort=sort_by,
                         listing_count=len(listings))

@app.route('/api/listings')
def api_listings():
    """API endpoint for getting listings data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    filter_type = request.args.get('filter', 'all')

    # Build query based on filter
    if filter_type == 'manual':
        where_clause = "WHERE is_manual = 1 AND (is_first_gen IS NULL OR is_first_gen = 0)"
    elif filter_type == 'first_gen':
        where_clause = "WHERE is_first_gen = 1"
    elif filter_type == 'auto':
        where_clause = "WHERE is_manual = 0"
    else:
        where_clause = "WHERE 1=1"

    cursor.execute(f"""
        SELECT * FROM listings
        {where_clause}
        ORDER BY price ASC
    """)

    listings = []
    for row in cursor.fetchall():
        category = "Unknown"
        if row.get('is_first_gen'):
            category = "1st Gen"
        elif row.get('is_manual'):
            category = "Manual"
        else:
            category = "Automatic"

        listings.append({
            'vin': row['vin'],
            'year': row['year'],
            'price': row['price'],
            'price_formatted': format_price(row['price']),
            'mileage': row['mileage'],
            'mileage_formatted': format_mileage(row['mileage']),
            'location': f"{row['city'] or 'Unknown'}, {row['state'] or 'Unknown'}",
            'dealer': row['dealer_name'] or 'Unknown',
            'transmission': row['transmission_type'] or 'Unknown',
            'category': category,
            'confidence': row.get('vin_pattern_confidence', 0),
            'days_on_market': calculate_days_on_market(row['first_seen']) if row['first_seen'] else 0
        })

    conn.close()
    return jsonify(listings)

@app.route('/api/stats')
def api_stats():
    """API endpoint for getting summary statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN is_manual = 1 AND (is_first_gen IS NULL OR is_first_gen = 0) THEN 1 END) as manual,
            COUNT(CASE WHEN is_first_gen = 1 THEN 1 END) as first_gen,
            COUNT(CASE WHEN is_manual = 0 THEN 1 END) as automatic,
            AVG(CASE WHEN price > 0 THEN price END) as avg_price,
            AVG(CASE WHEN mileage > 0 THEN mileage END) as avg_mileage
        FROM listings
    """)

    stats = cursor.fetchone()
    conn.close()

    return jsonify({
        'total': stats['total'],
        'manual': stats['manual'],
        'first_gen': stats['first_gen'],
        'automatic': stats['automatic'],
        'avg_price': int(stats['avg_price']) if stats['avg_price'] else 0,
        'avg_mileage': int(stats['avg_mileage']) if stats['avg_mileage'] else 0
    })

@app.route('/refresh')
def refresh():
    """Run a new search"""
    try:
        from main import FourRunnerHunter
        app.logger.info("Starting new 4Runner search...")

        hunter = FourRunnerHunter()
        stats = hunter.search_4runners_vin_focused()  # Updated method name

        app.logger.info(f"Search completed: {stats}")
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f"Search completed! Found {stats.get('new_manual_finds', 0)} new manual transmissions and {stats.get('new_first_gen_finds', 0)} new 1st gen 4Runners."
        })

    except Exception as e:
        app.logger.error(f"Search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Search failed. Check the logs for details."
        }), 500

@app.route('/vehicle/<vin>')
def vehicle_detail(vin):
    """Detailed view of a specific vehicle"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM listings WHERE vin = ?", (vin,))
    row = cursor.fetchone()

    if not row:
        return "Vehicle not found", 404

    # Parse raw data
    try:
        listing_data = json.loads(row['raw_listing_data']) if row['raw_listing_data'] else {}
        vin_data = json.loads(row['raw_vin_data']) if 'raw_vin_data' in row.keys() and row['raw_vin_data'] else {}
    except (json.JSONDecodeError, TypeError):
        listing_data = {}
        vin_data = {}
    
    # Generate dealer search URL
    dealer_name = row['dealer_name'] or ''
    city = row['city'] or ''
    state = row['state'] or ''
    dealer_search_url = None
    if dealer_name and (city or state):
        # Use city and state for location
        location = f"{city}, {state}" if city else state
        # Use Google search
        dealer_search_url = f"https://www.google.com/search?q={dealer_name}, {location}"

    vehicle = {
        'vin': row['vin'],
        'year': row['year'],
        'price': row['price'],
        'price_formatted': format_price(row['price']),
        'mileage': row['mileage'],
        'mileage_formatted': format_mileage(row['mileage']),
        'location': f"{row['city'] or 'Unknown'}, {row['state'] or 'Unknown'}",
        'dealer_name': row['dealer_name'],
        'transmission_type': row['transmission_type'],
        'engine_info': format_engine_display(row['engine_info'] if 'engine_info' in row.keys() else None),
        'is_manual': row['is_manual'] if 'is_manual' in row.keys() else False,
        'is_first_gen': row['is_first_gen'] if 'is_first_gen' in row.keys() else False,
        'manual_source': row['manual_source'] if 'manual_source' in row.keys() else None,
        'confidence': row['vin_pattern_confidence'] if 'vin_pattern_confidence' in row.keys() else 0,
        'model_code': row['model_code'] if 'model_code' in row.keys() else None,
        'analysis_reason': row['vin_analysis_reason'] if 'vin_analysis_reason' in row.keys() else None,
        'first_seen': row['first_seen'],
        'last_seen': row['last_seen'],
        'days_on_market': calculate_days_on_market(row['first_seen']) if row['first_seen'] else 0,
        'photos': listing_data.get('photoUrls', []),
        'dealer_url': listing_data.get('clickoffUrl'),
        'auto_dev_url': _construct_auto_dev_url(row, listing_data),
        'vin_decode_data': vin_data,
        'distance_from_origin': row['distance_from_origin'] if 'distance_from_origin' in row.keys() else None,
        'created_at': row['created_at'] if 'created_at' in row.keys() else None,
        'color_options': row['color_options'] if 'color_options' in row.keys() else None,
        'exterior_color': row['exterior_color'] if 'exterior_color' in row.keys() else listing_data.get('displayColor'),
        'interior_color': row['interior_color'] if 'interior_color' in row.keys() else listing_data.get('interiorColor'),
        'dealer_search_url': dealer_search_url,
        'raw_listing_json': json.dumps(listing_data, indent=2) if listing_data else None
    }

    conn.close()
    return render_template('vehicle_detail.html', vehicle=vehicle)

@app.route('/api/mark-seen/<vin>', methods=['POST'])
def mark_seen(vin):
    """Mark a vehicle as seen"""
    try:
        from database import Database
        db = Database()
        db.mark_as_seen(vin)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toggle-watch/<vin>', methods=['POST'])
def toggle_watch(vin):
    """Toggle watched status for a vehicle"""
    try:
        from database import Database
        db = Database()
        
        # Get current status
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_watched FROM listings WHERE vin = ?", (vin,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            current_status = row['is_watched'] if 'is_watched' in row.keys() else False
            db.mark_as_watched(vin, not current_status)
            return jsonify({'success': True, 'is_watched': not current_status})
        else:
            return jsonify({'success': False, 'error': 'Vehicle not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

def check_initial_data():
    """Check if database has data, run initial search if empty"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM listings")
        result = cursor.fetchone()
        conn.close()
        
        if result['count'] == 0:
            print("Database is empty. Running initial search...")
            from main import FourRunnerHunter
            hunter = FourRunnerHunter()
            stats = hunter.search_4runners_vin_focused()
            print(f"Initial search complete! Found {stats.get('total_listings', 0)} listings.")
            print(f"  Manual transmissions: {stats.get('confirmed_manuals', 0)}")
            print(f"  1st Gen (1984-1989): {stats.get('first_gen_collected', 0)}")
        else:
            print(f"Database contains {result['count']} listings.")
    except Exception as e:
        print(f"Error checking initial data: {e}")

if __name__ == '__main__':
    print("Starting 4Runner Manual Hunter Web App...")
    print("Features:")
    print("  - View all target 4Runners (1984-2002)")
    print("  - Filter by: Manual, 1st Gen, Automatic, Generation, Mileage")
    print("  - Sort by: Price, Year, Mileage, Days on Market")
    print("  - API endpoints for data access")
    print("  - Manual search refresh")
    print("")
    
    # Check for initial data
    check_initial_data()
    
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
