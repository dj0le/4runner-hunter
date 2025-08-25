#!/usr/bin/env python3
"""
Mechanic Report Generator - Creates structured markdown reports from virtual mechanic queries
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from virtual_mechanic import VirtualMechanic
from config import VEHICLE_SPECS

class MechanicReportGenerator:
    def __init__(self, reports_dir: str = "reports"):
        """Initialize report generator with output directory."""
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.mechanic = VirtualMechanic()
        
    def generate_fluid_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive fluid specifications report."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"fluid_specifications_{timestamp}.md"
        
        report_path = self.reports_dir / output_file
        
        # Define fluid queries
        fluid_queries = [
            {
                "title": "Engine Oil",
                "queries": [
                    "engine oil capacity viscosity 3VZ-E API grade specifications",
                    "engine oil drain refill capacity SG multigrade",
                    "oil filter change specifications 3VZ-E"
                ],
                "icon": "🛢️"
            },
            {
                "title": "Manual Transmission Oil", 
                "queries": [
                    "manual transmission oil capacity viscosity 5-speed",
                    "transmission gear oil GL-4 GL-5 specifications",
                    "R150F transmission oil capacity"
                ],
                "icon": "⚙️"
            },
            {
                "title": "Transfer Case Oil",
                "queries": [
                    "transfer case oil capacity viscosity 4WD GL-4 GL-5",
                    "transfer oil 75W-80 specifications",
                    "4WD transfer case fluid capacity"
                ],
                "icon": "🔄"
            },
            {
                "title": "Differential Oil",
                "queries": [
                    "differential oil grade GL-5 hypoid gear oil viscosity",
                    "front rear differential oil capacity SAE 90 80W-90",
                    "differential gear oil specifications 4x4"
                ],
                "icon": "⚙️"
            },
            {
                "title": "Coolant System",
                "queries": [
                    "coolant capacity radiator system cooling 3VZ-E",
                    "antifreeze ethylene glycol specifications",
                    "cooling system capacity drain refill"
                ],
                "icon": "🌡️"
            },
            {
                "title": "Brake Fluid",
                "queries": [
                    "brake fluid DOT specification hydraulic system",
                    "brake fluid capacity master cylinder",
                    "hydraulic brake system specifications"
                ],
                "icon": "🛑"
            },
            {
                "title": "Power Steering Fluid",
                "queries": [
                    "power steering fluid ATF Dexron specifications",
                    "steering system fluid capacity",
                    "hydraulic power steering oil"
                ],
                "icon": "🔄"
            }
        ]
        
        # Collect all results for analysis
        all_fluid_results = {}
        
        for fluid_category in fluid_queries:
            # Collect all results for this fluid category
            all_results = []
            for query in fluid_category['queries']:
                results = self.mechanic.search_manuals(query, n_results=3)
                all_results.extend(results)
            
            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            top_results = unique_results[:1]  # Just top result for reference
            
            all_fluid_results[fluid_category['title']] = top_results
        
        # Generate report content with summary only
        report_content = self._generate_report_header()
        report_content += self._generate_summary_section(all_fluid_results)
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def generate_maintenance_report(self, maintenance_items: List[str], output_file: Optional[str] = None) -> str:
        """Generate maintenance procedure report for specific items."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"maintenance_procedures_{timestamp}.md"
        
        report_path = self.reports_dir / output_file
        
        report_content = self._generate_report_header()
        report_content += "\n# Maintenance Procedures\n\n"
        
        for item in maintenance_items:
            report_content += f"\n## 🔧 {item}\n\n"
            
            # Search for the maintenance item
            results = self.mechanic.search_manuals(f"{item} procedure maintenance 3VZ-E", n_results=5)
            
            if results:
                for i, result in enumerate(results, 1):
                    manual_name = result['manual']
                    content = result['content']
                    score = result.get('vehicle_relevance_score', result['similarity_score'])
                    
                    clean_content = content.replace('---', '').strip()
                    if len(clean_content) > 500:
                        clean_content = clean_content[:500] + "..."
                    
                    # Extract page reference for PDF extraction
                    page_match = re.search(r'Page (\d+)', content)
                    page_ref = f", Page {page_match.group(1)}" if page_match else ""
                    
                    report_content += f"**{i}. From {manual_name}** (relevance: {score:.3f})\n"
                    if page_ref:
                        report_content += f"**Reference**: {manual_name}{page_ref}\n\n"
                    report_content += f"{clean_content}\n\n"
            else:
                report_content += "_No specific procedure found in indexed manuals._\n\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def generate_troubleshooting_report(self, symptoms: List[str], output_file: Optional[str] = None) -> str:
        """Generate troubleshooting report for specific symptoms."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"troubleshooting_{timestamp}.md"
        
        report_path = self.reports_dir / output_file
        
        report_content = self._generate_report_header()
        report_content += "\n# Troubleshooting Guide\n\n"
        
        for symptom in symptoms:
            report_content += f"\n## 🔍 {symptom}\n\n"
            
            # Search for troubleshooting information
            results = self.mechanic.search_manuals(f"{symptom} troubleshooting diagnosis 3VZ-E", n_results=5)
            
            if results:
                for i, result in enumerate(results, 1):
                    manual_name = result['manual']
                    content = result['content']
                    score = result.get('vehicle_relevance_score', result['similarity_score'])
                    
                    clean_content = content.replace('---', '').strip()
                    if len(clean_content) > 500:
                        clean_content = clean_content[:500] + "..."
                    
                    # Extract page reference for PDF extraction
                    page_match = re.search(r'Page (\d+)', content)
                    page_ref = f", Page {page_match.group(1)}" if page_match else ""
                    
                    report_content += f"**{i}. From {manual_name}** (relevance: {score:.3f})\n"
                    if page_ref:
                        report_content += f"**Reference**: {manual_name}{page_ref}\n\n"
                    report_content += f"{clean_content}\n\n"
            else:
                report_content += "_No specific troubleshooting information found in indexed manuals._\n\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def _generate_report_header(self) -> str:
        """Generate standard report header."""
        vehicle_info = self.mechanic.get_vehicle_info()
        coverage = self.mechanic.get_manual_coverage()
        
        header = f"""# Toyota 4Runner Virtual Mechanic Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Vehicle Information
- **Make**: {vehicle_info['make']}
- **Model**: {vehicle_info['model']} 
- **Year**: {vehicle_info['year']}
- **Generation**: {vehicle_info['generation']}
- **Series**: {vehicle_info['series']}
- **Engine**: {vehicle_info['engine']}
- **Transmission**: {vehicle_info['transmission']}
- **Drive Type**: {vehicle_info['drive_type']}

## Manual Coverage
- **Total indexed sections**: {coverage['total_chunks']}
- **Vehicle-specific data**: {'✅ Available' if coverage['vehicle_match'] else '❌ Limited'}
- **Manual types available**: {', '.join(coverage['manual_types'].keys())}

---
"""
        return header
    
    def _generate_summary_section(self, fluid_results: Dict[str, List[Dict]]) -> str:
        """Generate summary section with extracted specifications and manual references."""
        summary = """
<div style="page-break-after: always;"></div>

## 📋 Quick Reference Fluid Checklist

*Check off each fluid as you service it:*

"""
        
        # Extract specifications from search results
        specs = self._extract_fluid_specifications(fluid_results)
        
        for fluid_type, info in specs.items():
            summary += f"### ☐ {fluid_type}\n"
            if info['specification']:
                summary += f"- **Specification**: {info['specification']}\n"
            if info['capacity']:
                summary += f"- **Capacity**: {info['capacity']}\n"
            if info['manual_reference']:
                summary += f"- **Reference**: {info['manual_reference']}\n"
            summary += "\n"
        
        summary += """
### Service Notes
- ☐ Vehicle has been sitting 10 years - replace ALL fluids
- ☐ Check for leaks after filling
- ☐ Run engine and recheck levels
- ☐ Dispose of old fluids properly

---
*Specifications extracted from Toyota factory service manuals*
"""
        return summary
    
    def _extract_fluid_specifications(self, fluid_results: Dict[str, List[Dict]]) -> Dict:
        """Extract specific fluid specifications from search results."""
        specs = {
            "Engine Oil": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Manual Transmission": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Transfer Case": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Front Differential": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Rear Differential": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Coolant System": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Brake Fluid": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            },
            "Power Steering": {
                "specification": "",
                "capacity": "",
                "manual_reference": ""
            }
        }
        
        # Parse results to extract specifications
        for category, results in fluid_results.items():
            if results:
                top_result = results[0]
                content = top_result.get('content', '')
                metadata = top_result.get('metadata', {})
                
                # Extract manual and page reference
                manual_name = top_result.get('manual', 'Unknown Manual')
                page_match = re.search(r'Page (\d+)', content)
                page_num = page_match.group(1) if page_match else "N/A"
                
                # Map category to spec key
                spec_key = self._map_category_to_spec(category)
                if spec_key and spec_key in specs:
                    # Extract specifications from content
                    spec_info = self._parse_specifications(content, category)
                    specs[spec_key]['specification'] = spec_info.get('type', '')
                    specs[spec_key]['capacity'] = spec_info.get('capacity', '')
                    specs[spec_key]['manual_reference'] = f"{manual_name}, Page {page_num}"
        
        return specs
    
    def _map_category_to_spec(self, category: str) -> str:
        """Map fluid category to specification key."""
        mapping = {
            "Engine Oil": "Engine Oil",
            "Manual Transmission Oil": "Manual Transmission",
            "Transfer Case Oil": "Transfer Case",
            "Differential Oil": "Rear Differential",
            "Coolant System": "Coolant System",
            "Brake Fluid": "Brake Fluid",
            "Power Steering Fluid": "Power Steering"
        }
        return mapping.get(category, "")
    
    def _parse_specifications(self, content: str, category: str) -> Dict:
        """Parse content to extract fluid type and capacity."""
        import re
        
        spec_info = {"type": "", "capacity": ""}
        
        # Engine Oil patterns
        if "API" in content and "SG" in content:
            spec_info['type'] = "API SG multigrade (modern: 5W-30 or 10W-30)"
        
        # Category-specific parsing
        if "differential" in category.lower():
            # Look for GL-5 specifically for differentials
            if "GL-5" in content or "GL–5" in content:
                spec_info['type'] = "GL-5 hypoid gear oil"
                viscosity_match = re.search(r'(SAE \d+W?-?\d*|80W-90|SAE 90)', content)
                if viscosity_match:
                    spec_info['type'] += f", {viscosity_match.group(1)}"
        elif "transfer" in category.lower():
            # Check for transfer case specs
            if "GL-4" in content or "GL–4" in content or "GL-5" in content or "GL–5" in content:
                gl_match = re.search(r'(GL-[45]|GL–[45])', content)
                if gl_match:
                    spec_info['type'] = gl_match.group(1).replace('–', '-')
                    if "75W-80" in content or "75W–80" in content:
                        spec_info['type'] += ", SAE 75W-80"
        else:
            # GL-4/GL-5 patterns
            gl_match = re.search(r'(GL-[45]|AN GL-[45])', content)
            if gl_match:
                spec_info['type'] = gl_match.group(1)
                
            # Viscosity patterns
            viscosity_match = re.search(r'(SAE \d+W?-?\d*|75W-80|80W-90|SAE 90)', content)
            if viscosity_match and spec_info['type']:
                spec_info['type'] += f", {viscosity_match.group(1)}"
            elif viscosity_match:
                spec_info['type'] = viscosity_match.group(1)
        
        # Capacity patterns
        capacity_match = re.search(r'(\d+\.?\d*)\s*(liters?|US qts?|Imp\.? qts?)', content)
        if capacity_match:
            spec_info['capacity'] = f"{capacity_match.group(1)} {capacity_match.group(2)}"
        
        # Special cases
        if "DOT" in content:
            dot_match = re.search(r'DOT\s*(\d)', content)
            if dot_match:
                spec_info['type'] = f"DOT {dot_match.group(1)}"
        
        if "Dexron" in content or "ATF" in content:
            spec_info['type'] = "ATF Dexron II/III"
        
        if "ethylene glycol" in content.lower():
            spec_info['type'] = "Ethylene glycol antifreeze (50/50 mix)"
        
        return spec_info
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results and rank by relevance."""
        seen_content = set()
        unique_results = []
        
        for result in results:
            content_key = result['content'][:100]  # Use first 100 chars as dedup key
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.get('vehicle_relevance_score', x['similarity_score']), reverse=True)
        return unique_results


def main():
    """Generate sample reports."""
    generator = MechanicReportGenerator()
    
    print("Toyota 4Runner Report Generator")
    print("=" * 40)
    
    # Generate fluid specifications report
    print("Generating fluid specifications report...")
    fluid_report = generator.generate_fluid_report()
    print(f"✅ Fluid report saved: {fluid_report}")
    
    # Generate maintenance report
    maintenance_items = [
        "Timing Belt Replacement",
        "Oil Change Procedure", 
        "Brake Pad Replacement",
        "Coolant System Flush",
        "Transmission Oil Change"
    ]
    
    print("\nGenerating maintenance procedures report...")
    maintenance_report = generator.generate_maintenance_report(maintenance_items)
    print(f"✅ Maintenance report saved: {maintenance_report}")
    
    # Generate troubleshooting report
    symptoms = [
        "Engine won't start",
        "Overheating",
        "Hard shifting",
        "Brake pedal soft",
        "Steering vibration"
    ]
    
    print("\nGenerating troubleshooting report...")
    troubleshooting_report = generator.generate_troubleshooting_report(symptoms)
    print(f"✅ Troubleshooting report saved: {troubleshooting_report}")
    
    print(f"\nAll reports saved to: {generator.reports_dir}")


if __name__ == "__main__":
    main()