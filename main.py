#!/usr/bin/env python3
"""VIN-focused 4Runner manual transmission hunter (1984-2002)"""
import logging
from typing import Dict, List, Optional
from api_client import AutoDevAPI
from database import Database
from vin_analyzer import Toyota4RunnerVINAnalyzer

logger = logging.getLogger(__name__)

class FourRunnerHunter:
    """VIN-focused manual transmission hunter (1984-2002)"""

    def __init__(self):
        self.api_client = AutoDevAPI()
        self.database = Database()
        self.vin_analyzer = Toyota4RunnerVINAnalyzer()

    def search_4runners_vin_focused(self) -> Dict:
        """
        New VIN-focused search flow (1984-2002):
        1. Get all 4Runner listings
        2. Filter to 1984-2002 only (ignore 2003+)
        3. Collect ALL 1st gen (1984-1989) regardless of transmission
        4. Analyze 2nd/3rd gen (1990-2002) VINs for manual transmission codes
        5. Store results and notify
        """
        logger.info("Starting VIN-focused 4Runner search (1984-2002)...")

        stats = {
            "total_listings": 0,
            "filtered_out_modern": 0,
            "first_gen_collected": 0,
            "manual_candidates": 0,
            "confirmed_manuals": 0,
            "api_calls_saved": 0,
            "new_manual_finds": 0,
            "new_first_gen_finds": 0
        }

        # Step 1: Get all listings
        listings = self.api_client.get_all_4runner_listings()
        stats["total_listings"] = len(listings)

        if not listings:
            logger.warning("No listings found!")
            return stats

        logger.info(f"Found {len(listings)} total listings")

        # Step 2: VIN pattern analysis with year filtering
        vin_results = self.vin_analyzer.batch_analyze_vins(listings)

        manual_candidates = vin_results["manual_candidates"]
        auto_confirmed = vin_results["automatic_confirmed"]
        needs_api_verification = vin_results["needs_api_verification"]
        outside_target_years = vin_results["outside_target_years"]

        # Update stats
        stats["filtered_out_modern"] = len(outside_target_years)
        stats["manual_candidates"] = len(manual_candidates)
        stats["first_gen_collected"] = vin_results["summary"]["first_gen_collected"]
        stats["api_calls_saved"] = len(auto_confirmed) + len(outside_target_years)

        logger.info(f"VIN Analysis Results:")
        logger.info(f"  Total in target years (1984-2002): {stats['total_listings'] - stats['filtered_out_modern']}")
        logger.info(f"  Filtered out (2003+): {stats['filtered_out_modern']}")
        logger.info(f"  1st Gen collected (1984-1989): {stats['first_gen_collected']}")
        logger.info(f"  Manual candidates (2nd/3rd gen): {len(manual_candidates) - stats['first_gen_collected']}")
        logger.info(f"  Auto confirmed: {len(auto_confirmed)}")
        logger.info(f"  Needs API verification: {len(needs_api_verification)}")
        logger.info(f"  API calls saved: {stats['api_calls_saved']}")

        # Step 3: Process ALL listings with VIN decode for complete data
        new_manual_finds = []
        new_first_gen_finds = []
        
        # Combine all listings to process with VIN decode
        all_listings_to_process = manual_candidates + needs_api_verification + auto_confirmed
        
        for listing in all_listings_to_process:
            analysis = listing["vin_analysis"]
            vin = listing["vin"]
            
            # Check if this VIN already exists in database
            existing_vins = self.database.get_processed_vins()
            if vin in existing_vins:
                logger.debug(f"Skipping existing VIN: {vin}")
                continue
            
            logger.info(f"Processing new VIN: {vin} ({analysis['year']}) - {analysis['reason']}")
            
            # Always run VIN decode for new listings to get complete data
            logger.info(f"  Running VIN decode for complete vehicle data...")
            vin_data = self.api_client.decode_vin(vin)
            vehicle_info = self.create_vehicle_info_with_decode(listing, analysis, vin_data)
            
            # Override transmission detection based on VIN patterns for known types
            if analysis["is_first_gen"]:
                vehicle_info["is_manual"] = True  # 1st gen - collect all
                vehicle_info["manual_source"] = "FIRST_GEN_COLLECTION"
                vehicle_info["is_first_gen"] = True
            elif analysis["confidence"] >= 90 and analysis["is_manual_candidate"]:
                vehicle_info["is_manual"] = True
                vehicle_info["manual_source"] = "VIN_PATTERN_CONFIRMED_BY_API"
            elif analysis["confidence"] >= 90 and not analysis["is_manual_candidate"]:
                vehicle_info["is_manual"] = False
                vehicle_info["manual_source"] = "VIN_PATTERN_AUTO_CONFIRMED_BY_API"
            # For low confidence, rely on API decode data (handled in create_vehicle_info_with_decode)

            # Store in database
            is_new = self.database.upsert_listing(vehicle_info)
            if is_new:
                if vehicle_info.get("is_manual"):
                    new_manual_finds.append(vehicle_info)
                    stats["new_manual_finds"] += 1
                    stats["confirmed_manuals"] += 1
                    
                if analysis["is_first_gen"]:
                    new_first_gen_finds.append(vehicle_info)
                    stats["new_first_gen_finds"] += 1
                    
                # Log patterns for research
                if analysis["confidence"] < 80:
                    manual_status = "MANUAL" if vehicle_info.get("is_manual") else "AUTO"
                    logger.info(f"RESEARCH: Pattern {analysis['model_code']} for year {analysis['year']} = {manual_status}")

        # Step 4: Log filtered vehicles (for debugging)
        if outside_target_years:
            sample_filtered = outside_target_years[:3]  # Show first 3 as examples
            logger.info(f"Filtered out {len(outside_target_years)} vehicles from 2003+:")
            for listing in sample_filtered:
                year = self.vin_analyzer.decode_year_from_vin(listing.get("vin", ""))
                logger.info(f"  {listing.get('vin')} ({year}) - Outside target range")

        # Log new finds
        total_new_finds = new_manual_finds + new_first_gen_finds
        if total_new_finds:
            logger.info(f"Found {len(total_new_finds)} new target 4Runners!")
            logger.info(f"  Manual transmissions: {len(new_manual_finds)}")
            logger.info(f"  1st Gen (any transmission): {len(new_first_gen_finds)}")

        # Log summary statistics
        logger.info("VIN Analysis Summary:")
        summary = vin_results["summary"]
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")

        return stats

    def identify_4runner_engine(self, engine_data: Dict) -> Optional[str]:
        """Identify the Toyota 4Runner engine code from VIN decode data."""
        if not engine_data:
            return None
        
        cylinders = engine_data.get('cylinder', 0)
        size = engine_data.get('size', 0)
        configuration = engine_data.get('configuration', '').upper()
        
        # Map to Toyota engine codes
        if cylinders == 4 and size == 2.4:
            return "22R-E"
        elif cylinders == 4 and size == 2.7:
            return "3RZ-FE"
        elif cylinders == 6 and configuration == 'V' and size == 3.0:
            return "3VZ-E"
        elif cylinders == 6 and configuration == 'V' and size == 3.4:
            return "5VZ-FE"
        
        return None

    def create_vehicle_info_from_listing(self, listing: Dict, analysis: Dict) -> Dict:
        """Create vehicle info from listing and VIN analysis"""
        return {
            "vin": listing["vin"],
            "year": analysis["year"],
            "price": self.parse_price(listing.get("price")),
            "mileage": self.parse_mileage(listing.get("mileage")),
            "city": listing.get("city"),
            "state": listing.get("state"),
            "dealer_name": listing.get("dealerName"),
            "transmission_type": analysis["transmission_type"],
            "vin_pattern_confidence": analysis["confidence"],
            "vin_analysis_reason": analysis["reason"],
            "model_code": analysis.get("model_code", "Unknown"),
            "is_first_gen": analysis.get("is_first_gen", False),
            "exterior_color": listing.get("displayColor"),
            "interior_color": listing.get("interiorColor"),
            "distance_from_origin": listing.get("distanceFromOrigin"),
            "created_at": listing.get("createdAt"),
            "raw_listing_data": listing
        }

    def create_vehicle_info_with_decode(self, listing: Dict, analysis: Dict, vin_data: Dict) -> Dict:
        """Create vehicle info from listing, VIN analysis, and API decode"""
        vehicle_info = self.create_vehicle_info_from_listing(listing, analysis)

        if vin_data:
            # Extract transmission info from API response
            transmission = vin_data.get("transmission", {})
            api_trans_type = transmission.get("transmissionType", "").upper()

            # Check if API confirms manual
            api_is_manual = "MANUAL" in api_trans_type

            # Combine VIN pattern and API analysis
            if api_is_manual and analysis["confidence"] >= 50:
                vehicle_info["is_manual"] = True
                vehicle_info["manual_source"] = "VIN_PATTERN_AND_API"
                vehicle_info["api_transmission_type"] = api_trans_type
            elif api_is_manual:
                vehicle_info["is_manual"] = True
                vehicle_info["manual_source"] = "API_ONLY"
                vehicle_info["api_transmission_type"] = api_trans_type
            else:
                vehicle_info["is_manual"] = False
                vehicle_info["manual_source"] = "API_CONFIRMS_AUTO"
                vehicle_info["api_transmission_type"] = api_trans_type

            # Extract color options from VIN decode data
            colors = vin_data.get("colors", [])
            color_options = []
            for color_category in colors:
                category_name = color_category.get("category", "")
                for option in color_category.get("options", []):
                    color_name = option.get("name", "")
                    if color_name:
                        color_options.append(f"{category_name}: {color_name}")
            
            if color_options:
                vehicle_info["color_options"] = "; ".join(color_options)
                
            # Extract engine information
            engine = vin_data.get("engine", {})
            if engine:
                engine_parts = []
                
                # Identify the engine code
                engine_code = self.identify_4runner_engine(engine)
                if engine_code:
                    engine_parts.append(engine_code)
                
                # Add basic specs
                if engine.get("size"):
                    engine_parts.append(f"{engine.get('size')}L")
                if engine.get("configuration") and engine.get("cylinder"):
                    engine_parts.append(f"{engine.get('configuration')}{engine.get('cylinder')}")
                if engine.get("fuelType"):
                    engine_parts.append(engine.get("fuelType"))
                if engine.get("horsepower"):
                    engine_parts.append(f"{engine.get('horsepower')} HP")
                if engine.get("torque"):
                    engine_parts.append(f"{engine.get('torque')} lb-ft")
                
                if engine_parts:
                    vehicle_info["engine_info"] = " ".join(engine_parts)
            
            vehicle_info["raw_vin_data"] = vin_data
        else:
            # VIN decode failed, rely on pattern
            if analysis["confidence"] >= 70:
                vehicle_info["is_manual"] = True
                vehicle_info["manual_source"] = "VIN_PATTERN_ONLY"
                logger.warning(f"VIN decode failed for {listing['vin']}, relying on pattern analysis")
            else:
                vehicle_info["is_manual"] = False
                vehicle_info["manual_source"] = "VIN_DECODE_FAILED"

        return vehicle_info

    def parse_price(self, price_str) -> int:
        """Parse price string to integer"""
        if not price_str:
            return 0

        if isinstance(price_str, (int, float)):
            return int(price_str)

        price_clean = str(price_str).replace("$", "").replace(",", "")
        try:
            return int(float(price_clean))
        except (ValueError, TypeError):
            return 0

    def parse_mileage(self, mileage_str) -> int:
        """Parse mileage string to integer"""
        if not mileage_str:
            return 0

        if isinstance(mileage_str, (int, float)):
            return int(mileage_str)

        mileage_clean = str(mileage_str).replace(",", "").replace(" Miles", "").replace("mi", "")
        try:
            return int(float(mileage_clean))
        except (ValueError, TypeError):
            return 0


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    hunter = FourRunnerHunter()
    stats = hunter.search_4runners_vin_focused()

    logger.info(f"Search complete!")
    logger.info(f"Total listings: {stats['total_listings']}")
    logger.info(f"Filtered out (2001+): {stats['filtered_out_modern']}")
    logger.info(f"1st Gen collected: {stats['first_gen_collected']}")
    logger.info(f"Manual candidates: {stats['manual_candidates']}")
    logger.info(f"New finds: {stats['new_manual_finds'] + stats['new_first_gen_finds']}")
    logger.info(f"API calls saved: {stats['api_calls_saved']}")
