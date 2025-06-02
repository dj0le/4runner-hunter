#!/usr/bin/env python3
"""Test the VIN analyzer with some sample VINs"""
import sys
sys.path.append('..')
from vin_analyzer import VINAnalyzer

def test_vin_analyzer():
    analyzer = VINAnalyzer()

    # Test VINs from your previous results
    test_vins = [
        "JT3HN86R4X0204713",  # 1999 - was flagged as manual
        "JT3HN86R7W0175125",  # 1998 - was flagged as manual
        "JT3GM84R7X0045803",  # 1999 - was flagged as manual
    ]

    for vin in test_vins:
        print(f"\nTesting VIN: {vin}")
        analysis = analyzer.analyze_manual_probability(vin)

        print(f"  Manual candidate: {analysis['is_manual_candidate']}")
        print(f"  Confidence: {analysis['confidence']}%")
        print(f"  Reason: {analysis['reason']}")
        print(f"  Year: {analysis['year']}")
        print(f"  Transmission: {analysis['transmission_type']}")

if __name__ == "__main__":
    test_vin_analyzer()
