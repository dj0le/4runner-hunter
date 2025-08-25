#!/usr/bin/env python3
"""
Extract Manual Pages - Smart extraction with visual reference sheets
"""

import os
import sys
from pathlib import Path
from pdf_page_extractor import PDFPageExtractor

def extract_with_preview(report_file: str):
    """Extract pages and create preview."""
    extractor = PDFPageExtractor()
    
    print(f"\n📚 Extracting manual pages from: {Path(report_file).name}")
    print("=" * 60)
    
    # First, show what will be extracted
    references = extractor._parse_report_references(report_file)
    
    if references:
        print("\n📋 Found references to extract:\n")
        total_pages = 0
        
        for ref in references:
            pages = ref['pages']
            total_pages += len(pages)
            print(f"  📖 {ref['context']}")
            print(f"     File: {ref['manual_file']}")
            print(f"     Pages: {', '.join(map(str, pages[:5]))}" + 
                  (f"... ({len(pages)} total)" if len(pages) > 5 else ""))
            print()
        
        print(f"Total pages to extract: {total_pages}")
        print("-" * 60)
        
        # Extract the pages
        output_file = extractor.extract_pages_from_report(report_file)
        
        if output_file:
            print(f"\n✅ Success! Extracted manual pages saved to:")
            print(f"   {output_file}")
            print(f"\n📊 This PDF includes:")
            print("   • All referenced pages from the report")
            print("   • Context pages (before/after) for better understanding")
            print("   • Original formatting, diagrams, and tables")
            print(f"\n🖨️ Ready to print: {Path(output_file).name}")
    else:
        print("❌ No manual page references found in this report.")
        print("\nTip: This tool works best with reports that include manual references")
        print("     like 'Reference: Factory Service Manual 1991, Page 123'")


def list_recent_reports():
    """List recent reports that can have pages extracted."""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("No reports directory found!")
        return []
    
    # Get markdown files sorted by modification time
    md_files = sorted(
        reports_dir.glob("*.md"), 
        key=lambda f: f.stat().st_mtime, 
        reverse=True
    )[:10]  # Last 10 reports
    
    if md_files:
        print("\n📄 Recent Reports:")
        print("=" * 60)
        for i, file in enumerate(md_files, 1):
            size = file.stat().st_size / 1024  # KB
            print(f"{i:2d}. {file.name} ({size:.1f} KB)")
        print()
    
    return md_files


def main():
    if len(sys.argv) < 2:
        print("\n🔧 Toyota 4Runner Manual Page Extractor")
        print("=" * 60)
        print("\nThis tool extracts actual PDF pages referenced in your reports,")
        print("preserving diagrams, tables, and original formatting.\n")
        
        reports = list_recent_reports()
        
        if reports:
            print("Usage:")
            print("  python extract_manual_pages.py <report_file>")
            print("  python extract_manual_pages.py <number>\n")
            print("Example:")
            print("  python extract_manual_pages.py reports/starting_system_diagnosis_20250605.md")
            print("  python extract_manual_pages.py 1")
        return
    
    report_arg = sys.argv[1]
    
    # Check if it's a number
    try:
        report_num = int(report_arg)
        reports = list_recent_reports()
        if 1 <= report_num <= len(reports):
            report_file = str(reports[report_num - 1])
        else:
            print(f"Invalid number. Choose between 1 and {len(reports)}")
            return
    except ValueError:
        report_file = report_arg
    
    if not Path(report_file).exists():
        print(f"Error: Report file not found: {report_file}")
        return
    
    extract_with_preview(report_file)


if __name__ == "__main__":
    main()