#!/usr/bin/env python3
"""VIN-based manual transmission detection for Toyota 4Runners (1984-2002)"""
import re
from typing import Dict, List, Tuple, Optional

class Toyota4RunnerVINAnalyzer:
    """Analyze Toyota 4Runner VINs for manual transmission patterns (1984-2002)"""

    def __init__(self):
        # Toyota 4Runner VIN Patterns - Positions 4-8 Analysis (1984-2002)
        self.manual_patterns = {
            "VN39W": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "5-Speed Manual", "confidence": 90},
            "VN39J": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "5-Speed Manual", "confidence": 90},
            "VN29V": {"years": [1995], "trans": "5-Speed Manual", "confidence": 85},
            "RN37W": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "5-Speed Manual", "confidence": 90},
            "LN130": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "5-Speed Manual", "confidence": 95},
            "RZN13": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "5-Speed Manual", "confidence": 95},
            "VZN13": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "5-Speed Manual", "confidence": 95},
            "RZN18": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "5-Speed Manual", "confidence": 85},
            "VZN18": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "5-Speed Manual", "confidence": 85},
        }

        self.automatic_patterns = {
            # 1990-1995 Generation 2 Automatic Patterns
            "LN130": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "4-Speed Auto", "confidence": 85},  # Some LN130 were auto
            "VZN13": {"years": [1990, 1991, 1992, 1993, 1994, 1995], "trans": "4-Speed Auto", "confidence": 85},  # Some VZN13 were auto

            # 1996-2002 Generation 3 Automatic Patterns
            "HN87R": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "4-Speed Auto", "confidence": 95},
            "HN86R": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "4-Speed Auto", "confidence": 95},  # API data is wrong - these are automatics!
            "GN86R": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "4-Speed Auto", "confidence": 95},
            "GN87R": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "4-Speed Auto", "confidence": 95},
            # GM84R removed - it's actually mixed manual/auto with no clear pattern!
            "VZN18": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "4-Speed Auto", "confidence": 70},  # Some VZN18 were auto
            "RZN18": {"years": [1996, 1997, 1998, 1999, 2000, 2001, 2002], "trans": "4-Speed Auto", "confidence": 70},  # Some RZN18 were auto
        }

        # Year decoding map
        self.year_map = {
            # 1980s-2000s
            'E': 1984, 'F': 1985, 'G': 1986, 'H': 1987, 'J': 1988, 'K': 1989,
            'L': 1990, 'M': 1991, 'N': 1992, 'P': 1993, 'R': 1994, 'S': 1995,
            'T': 1996, 'V': 1997, 'W': 1998, 'X': 1999, 'Y': 2000,
            '1': 2001, '2': 2002,
        }

        # Target year range
        self.MIN_YEAR = 1984
        self.MAX_YEAR = 2002
        self.FIRST_GEN_MAX_YEAR = 1989  # 1984-1989 = collect all regardless of transmission

    def decode_year_from_vin(self, vin: str) -> Optional[int]:
        """Decode model year from VIN position 10 (index 9)"""
        if len(vin) < 10:
            return None
        year_code = vin[9]
        return self.year_map.get(year_code)

    def extract_vin_pattern(self, vin: str) -> Optional[str]:
        """Extract the transmission-relevant pattern from VIN positions 4-8"""
        if len(vin) < 8:
            return None
        return vin[3:8]  # Positions 4-8 (0-indexed)

    def extract_vin_components(self, vin: str) -> Dict:
        """Extract key components from Toyota VIN"""
        if not vin or len(vin) != 17:
            return {"valid": False, "reason": "Invalid VIN length"}

        if not vin.startswith("JT3"):
            return {"valid": False, "reason": "Not a Toyota 4Runner VIN"}

        # Decode year first for filtering
        year = self.decode_year_from_vin(vin)

        # Filter out anything newer than 2002
        if not year or year > self.MAX_YEAR:
            return {"valid": False, "reason": f"Year {year} is outside target range (1984-2002)"}

        if year < self.MIN_YEAR:
            return {"valid": False, "reason": f"Year {year} is before 4Runner production started"}

        # Extract components
        wmi = vin[0:3]          # World Manufacturer ID
        model_code = vin[3:8]   # Model/Engine/Trans code
        check_digit = vin[8]    # Check digit
        year_code = vin[9]      # Model year
        plant_code = vin[10]    # Manufacturing plant
        serial = vin[11:17]     # Serial number

        return {
            "valid": True,
            "wmi": wmi,
            "model_code": model_code,
            "year_code": year_code,
            "year": year,
            "plant_code": plant_code,
            "serial": serial,
            "full_vin": vin,
            "is_first_gen": year <= self.FIRST_GEN_MAX_YEAR
        }

    def is_manual_transmission(self, vin: str) -> Tuple[bool, int, str]:
        """
        Check if VIN indicates manual transmission
        Returns: (is_manual, confidence, reason)
        """
        components = self.extract_vin_components(vin)

        if not components["valid"]:
            return False, 0, components["reason"]

        model_code = components["model_code"]
        year = components["year"]
        is_first_gen = components["is_first_gen"]

        # RULE 1: All 1st gen 4Runners (1984-1989) are collected regardless of transmission
        if is_first_gen:
            return True, 100, f"1st Gen 4Runner ({year}) - collecting all regardless of transmission"

        # RULE 2: Check against known manual patterns for 2nd/3rd gen
        for pattern, info in self.manual_patterns.items():
            if model_code == pattern and year in info["years"]:
                return True, info["confidence"], f"Pattern '{pattern}' matches {info['trans']}"

        # RULE 3: Check if it's a known automatic pattern
        for pattern, info in self.automatic_patterns.items():
            if model_code == pattern and year in info["years"]:
                return False, info["confidence"], f"Pattern '{pattern}' is {info['trans']}"

        # RULE 4: Unknown pattern for 2nd/3rd gen - needs API verification
        return False, 25, f"Unknown pattern '{model_code}' for year {year} - needs API verification"

    def analyze_manual_probability(self, vin: str) -> Dict:
        """Analyze VIN for manual transmission probability"""
        is_manual, confidence, reason = self.is_manual_transmission(vin)
        components = self.extract_vin_components(vin)

        if not components["valid"]:
            return {
                "is_manual_candidate": False,
                "confidence": 0,
                "reason": reason,
                "transmission_type": "Unknown",
                "year": None,
                "needs_api_check": False,
                "is_first_gen": False,
                "outside_target_years": True
            }

        return {
            "is_manual_candidate": is_manual,
            "confidence": confidence,
            "reason": reason,
            "transmission_type": self._get_transmission_type(components["model_code"], components["year"]),
            "year": components["year"],
            "model_code": components["model_code"],
            "needs_api_check": confidence < 80 and not components["is_first_gen"],  # 1st gen doesn't need API check
            "is_first_gen": components["is_first_gen"],
            "outside_target_years": False,
            "vin_components": components
        }

    def _get_transmission_type(self, model_code: str, year: int) -> str:
        """Get transmission type for a given model code and year"""
        # 1st gen - we collect all
        if year <= self.FIRST_GEN_MAX_YEAR:
            return "Any (1st Gen Collection)"

        # Check manual patterns first
        for pattern, info in self.manual_patterns.items():
            if model_code == pattern and year in info["years"]:
                return info["trans"]

        # Check automatic patterns
        for pattern, info in self.automatic_patterns.items():
            if model_code == pattern and year in info["years"]:
                return info["trans"]

        return "Unknown"

    def batch_analyze_vins(self, listings: List[Dict]) -> Dict:
        """Analyze a batch of listings for manual candidates (1984-2000 only)"""
        results = {
            "manual_candidates": [],          # High confidence manuals + all 1st gen
            "automatic_confirmed": [],       # High confidence automatics
            "needs_api_verification": [],    # Unknown patterns needing API check
            "invalid_vins": [],             # Bad VINs
            "outside_target_years": [],     # 2001+ vehicles (filtered out)
            "summary": {
                "total_processed": 0,
                "manual_found": 0,
                "automatic_found": 0,
                "needs_verification": 0,
                "invalid": 0,
                "first_gen_collected": 0,
                "outside_target_years": 0
            }
        }

        for listing in listings:
            vin = listing.get("vin")
            if not vin:
                results["invalid_vins"].append(listing)
                results["summary"]["invalid"] += 1
                continue

            analysis = self.analyze_manual_probability(vin)
            listing["vin_analysis"] = analysis
            results["summary"]["total_processed"] += 1

            # Filter out vehicles outside target years (2001+)
            if analysis["outside_target_years"]:
                results["outside_target_years"].append(listing)
                results["summary"]["outside_target_years"] += 1
                continue

            # Categorize based on analysis
            if analysis["is_manual_candidate"] and analysis["confidence"] >= 80:
                results["manual_candidates"].append(listing)
                results["summary"]["manual_found"] += 1

                # Track 1st gen separately
                if analysis["is_first_gen"]:
                    results["summary"]["first_gen_collected"] += 1

            elif analysis["needs_api_check"]:
                results["needs_api_verification"].append(listing)
                results["summary"]["needs_verification"] += 1
            else:
                results["automatic_confirmed"].append(listing)
                results["summary"]["automatic_found"] += 1

        return results

    def get_pattern_statistics(self) -> Dict:
        """Get statistics about known VIN patterns"""
        total_manual_years = sum(len(info["years"]) for info in self.manual_patterns.values())
        total_auto_years = sum(len(info["years"]) for info in self.automatic_patterns.values())

        return {
            "target_years": f"{self.MIN_YEAR}-{self.MAX_YEAR}",
            "first_gen_years": f"{self.MIN_YEAR}-{self.FIRST_GEN_MAX_YEAR}",
            "manual_patterns": len(self.manual_patterns),
            "automatic_patterns": len(self.automatic_patterns),
            "manual_year_combinations": total_manual_years,
            "automatic_year_combinations": total_auto_years,
            "last_manual_year": self.MAX_YEAR,
            "collect_all_first_gen": True
        }

# Example usage and testing
if __name__ == "__main__":
    analyzer = Toyota4RunnerVINAnalyzer()

    # Test VINs representing different scenarios
    test_vins = [
        "JT3VN39W4N8043298",  # 2022 - should be filtered out
        "JT3RN60L0F0123456",  # 1985 - 1st gen, should be collected
        "JT3HN87R3T0043862",  # 1996 - should be automatic
        "JT3LN130XL0012345",  # 1990 - could be manual
    ]

    print("Toyota 4Runner VIN Analysis Results (1984-2000 Only):")
    print("=" * 60)

    for vin in test_vins:
        result = analyzer.analyze_manual_probability(vin)
        print(f"\nVIN: {vin}")
        print(f"Year: {result['year']}")
        print(f"Manual Candidate: {result['is_manual_candidate']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Transmission: {result['transmission_type']}")
        print(f"1st Gen: {result['is_first_gen']}")
        print(f"Outside Target: {result['outside_target_years']}")
        print(f"Reason: {result['reason']}")

    print(f"\nPattern Statistics:")
    stats = analyzer.get_pattern_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
