import sqlite3
from datetime import datetime
import json
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.initialize_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(self):
        """Create tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Listings table with VIN analysis fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY,
                    vin TEXT UNIQUE,
                    year INTEGER,
                    price INTEGER,
                    mileage INTEGER,
                    city TEXT,
                    state TEXT,
                    dealer_name TEXT,
                    transmission_type TEXT,
                    transmission_speeds INTEGER,
                    engine_info TEXT,
                    drivetrain TEXT,
                    trim TEXT,
                    first_seen DATETIME,
                    last_seen DATETIME,
                    is_manual BOOLEAN,
                    notified BOOLEAN DEFAULT FALSE,

                    -- VIN Analysis fields
                    vin_pattern_confidence INTEGER,
                    vin_analysis_reason TEXT,
                    manual_source TEXT,
                    needs_research BOOLEAN DEFAULT FALSE,
                    api_transmission_type TEXT,
                    model_code TEXT,
                    is_first_gen BOOLEAN DEFAULT FALSE,

                    -- Raw data
                    raw_listing_data TEXT,
                    raw_vin_data TEXT,
                    
                    -- User tracking fields
                    is_seen BOOLEAN DEFAULT FALSE,
                    is_watched BOOLEAN DEFAULT FALSE,
                    seen_timestamp DATETIME,
                    watched_timestamp DATETIME,
                    
                    -- Additional fields from listing data
                    exterior_color TEXT,
                    interior_color TEXT,
                    distance_from_origin INTEGER,
                    created_at DATETIME,
                    color_options TEXT
                )
            """)

            # Add missing columns if they don't exist (for existing databases)
            self._add_missing_columns(cursor)

            # Search history table with additional stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_runs (
                    id INTEGER PRIMARY KEY,
                    run_timestamp DATETIME,
                    total_listings_found INTEGER,
                    new_listings INTEGER,
                    manual_listings_found INTEGER,
                    manual_candidates INTEGER,
                    api_calls_made INTEGER,
                    api_calls_saved INTEGER,
                    errors TEXT
                )
            """)

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vin ON listings(vin)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_manual ON listings(is_manual)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notified ON listings(notified)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_manual_source ON listings(manual_source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_needs_research ON listings(needs_research)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_year ON listings(year)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_first_gen ON listings(is_first_gen)")

            conn.commit()

    def _add_missing_columns(self, cursor):
        """Add missing columns to existing tables"""
        # Get existing columns
        cursor.execute("PRAGMA table_info(listings)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Add missing columns
        if 'model_code' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN model_code TEXT")

        if 'is_first_gen' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN is_first_gen BOOLEAN DEFAULT FALSE")
            
        if 'is_seen' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN is_seen BOOLEAN DEFAULT FALSE")
            
        if 'is_watched' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN is_watched BOOLEAN DEFAULT FALSE")
            
        if 'seen_timestamp' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN seen_timestamp DATETIME")
            
        if 'watched_timestamp' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN watched_timestamp DATETIME")
            
        if 'exterior_color' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN exterior_color TEXT")
            
        if 'interior_color' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN interior_color TEXT")
            
        if 'distance_from_origin' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN distance_from_origin INTEGER")
            
        if 'created_at' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN created_at DATETIME")
            
        if 'color_options' not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN color_options TEXT")

    def upsert_listing(self, listing_data: Dict) -> bool:
        """Insert or update a listing. Returns True if new listing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if VIN already exists
            cursor.execute("SELECT id FROM listings WHERE vin = ?", (listing_data['vin'],))
            existing = cursor.fetchone()

            now = datetime.now().isoformat()

            if existing:
                # Update existing listing
                cursor.execute("""
                    UPDATE listings SET
                        year = ?,
                        price = ?,
                        mileage = ?,
                        city = ?,
                        state = ?,
                        dealer_name = ?,
                        transmission_type = ?,
                        transmission_speeds = ?,
                        engine_info = ?,
                        drivetrain = ?,
                        trim = ?,
                        last_seen = ?,
                        is_manual = ?,
                        vin_pattern_confidence = ?,
                        vin_analysis_reason = ?,
                        manual_source = ?,
                        needs_research = ?,
                        api_transmission_type = ?,
                        model_code = ?,
                        is_first_gen = ?,
                        raw_listing_data = ?,
                        raw_vin_data = ?,
                        exterior_color = ?,
                        interior_color = ?,
                        distance_from_origin = ?,
                        created_at = ?,
                        color_options = ?
                    WHERE vin = ?
                """, (
                    listing_data.get('year'),
                    listing_data.get('price'),
                    listing_data.get('mileage'),
                    listing_data.get('city'),
                    listing_data.get('state'),
                    listing_data.get('dealer_name'),
                    listing_data.get('transmission_type'),
                    listing_data.get('transmission_speeds'),
                    listing_data.get('engine_info'),
                    listing_data.get('drivetrain'),
                    listing_data.get('trim'),
                    now,
                    listing_data.get('is_manual', False),
                    listing_data.get('vin_pattern_confidence'),
                    listing_data.get('vin_analysis_reason'),
                    listing_data.get('manual_source'),
                    listing_data.get('needs_research', False),
                    listing_data.get('api_transmission_type'),
                    listing_data.get('model_code'),
                    listing_data.get('is_first_gen', False),
                    json.dumps(listing_data.get('raw_listing_data', {})),
                    json.dumps(listing_data.get('raw_vin_data', {})),
                    listing_data.get('exterior_color'),
                    listing_data.get('interior_color'),
                    listing_data.get('distance_from_origin'),
                    listing_data.get('created_at'),
                    listing_data.get('color_options'),
                    listing_data['vin']
                ))
                conn.commit()
                return False
            else:
                # Insert new listing
                cursor.execute("""
                    INSERT INTO listings (
                        vin, year, price, mileage, city, state, dealer_name,
                        transmission_type, transmission_speeds, engine_info,
                        drivetrain, trim, first_seen, last_seen, is_manual,
                        vin_pattern_confidence, vin_analysis_reason, manual_source,
                        needs_research, api_transmission_type, model_code, is_first_gen,
                        raw_listing_data, raw_vin_data, exterior_color, interior_color,
                        distance_from_origin, created_at, color_options
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    listing_data['vin'],
                    listing_data.get('year'),
                    listing_data.get('price'),
                    listing_data.get('mileage'),
                    listing_data.get('city'),
                    listing_data.get('state'),
                    listing_data.get('dealer_name'),
                    listing_data.get('transmission_type'),
                    listing_data.get('transmission_speeds'),
                    listing_data.get('engine_info'),
                    listing_data.get('drivetrain'),
                    listing_data.get('trim'),
                    now,
                    now,
                    listing_data.get('is_manual', False),
                    listing_data.get('vin_pattern_confidence'),
                    listing_data.get('vin_analysis_reason'),
                    listing_data.get('manual_source'),
                    listing_data.get('needs_research', False),
                    listing_data.get('api_transmission_type'),
                    listing_data.get('model_code'),
                    listing_data.get('is_first_gen', False),
                    json.dumps(listing_data.get('raw_listing_data', {})),
                    json.dumps(listing_data.get('raw_vin_data', {})),
                    listing_data.get('exterior_color'),
                    listing_data.get('interior_color'),
                    listing_data.get('distance_from_origin'),
                    listing_data.get('created_at'),
                    listing_data.get('color_options')
                ))
                conn.commit()
                return True

    def get_unnotified_manual_listings(self) -> List[Dict]:
        """Get all manual transmission listings that haven't been notified yet."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM listings
                WHERE is_manual = TRUE AND notified = FALSE
                ORDER BY first_seen DESC
            """)

            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            return results

    def mark_as_notified(self, vin: str):
        """Mark a listing as notified."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings SET notified = TRUE WHERE vin = ?",
                (vin,)
            )
            conn.commit()

    def log_search_run(self, stats: Dict):
        """Log search run statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_runs (
                    run_timestamp, total_listings_found, new_listings,
                    manual_listings_found, manual_candidates, api_calls_made,
                    api_calls_saved, errors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                stats.get('total_listings', 0),
                stats.get('new_listings', 0),
                stats.get('confirmed_manuals', 0),
                stats.get('manual_candidates', 0),
                stats.get('api_calls_made', 0),
                stats.get('api_calls_saved', 0),
                json.dumps(stats.get('errors', []))
            ))
            conn.commit()

    def get_processed_vins(self) -> set:
        """Get set of all VINs already in database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT vin FROM listings")
            return {row[0] for row in cursor.fetchall()}

    def get_manual_listings_summary(self) -> List[Dict]:
        """Get summary of all manual transmission listings."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vin, year, price, mileage, city, state,
                       transmission_type, manual_source, vin_pattern_confidence,
                       first_seen, last_seen
                FROM listings
                WHERE is_manual = TRUE
                ORDER BY year DESC, price ASC
            """)

            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            return results

    def get_research_needed_listings(self) -> List[Dict]:
        """Get listings that need manual research."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vin, year, transmission_type, vin_analysis_reason,
                       city, state, price, mileage
                FROM listings
                WHERE needs_research = TRUE
                ORDER BY year DESC
            """)

            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            return results

    def get_stats_by_manual_source(self) -> Dict:
        """Get statistics grouped by manual detection source."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    manual_source,
                    COUNT(*) as count,
                    AVG(vin_pattern_confidence) as avg_confidence
                FROM listings
                WHERE manual_source IS NOT NULL
                GROUP BY manual_source
                ORDER BY count DESC
            """)

            results = {}
            for row in cursor.fetchall():
                results[row['manual_source']] = {
                    'count': row['count'],
                    'avg_confidence': row['avg_confidence']
                }
            return results
    
    def mark_as_seen(self, vin: str):
        """Mark a listing as seen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings SET is_seen = TRUE, seen_timestamp = ? WHERE vin = ?",
                (datetime.now().isoformat(), vin)
            )
            conn.commit()
    
    def mark_as_watched(self, vin: str, watched: bool = True):
        """Mark a listing as watched or unwatched."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if watched:
                cursor.execute(
                    "UPDATE listings SET is_watched = TRUE, watched_timestamp = ? WHERE vin = ?",
                    (datetime.now().isoformat(), vin)
                )
            else:
                cursor.execute(
                    "UPDATE listings SET is_watched = FALSE, watched_timestamp = NULL WHERE vin = ?",
                    (vin,)
                )
            conn.commit()
    
    def get_watched_listings(self) -> List[Dict]:
        """Get all watched listings."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM listings
                WHERE is_watched = TRUE
                ORDER BY watched_timestamp DESC
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            return results
