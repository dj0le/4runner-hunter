#!/usr/bin/env python3
"""
PDF Page Extractor - Extract specific pages from manuals based on report references
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2

class PDFPageExtractor:
    def __init__(self, manuals_dir: str = "manuals", output_dir: str = "extracted_pages"):
        """Initialize PDF page extractor."""
        self.manuals_dir = Path(manuals_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_pages_from_report(self, report_file: str) -> str:
        """Extract all referenced pages from a report."""
        # Parse report for manual references
        references = self._parse_report_references(report_file)
        
        if not references:
            print("No manual references found in report.")
            return ""
        
        # Create output filename based on report
        report_name = Path(report_file).stem
        output_pdf = self.output_dir / f"{report_name}_manual_pages.pdf"
        
        # Create PDF writer for combined output
        pdf_writer = PyPDF2.PdfWriter()
        
        # Track what we've extracted
        extracted_count = 0
        extraction_log = []
        
        for ref in references:
            manual_file = ref['manual_file']
            page_numbers = ref['pages']
            
            pdf_path = self.manuals_dir / manual_file
            if not pdf_path.exists():
                print(f"Warning: Manual not found: {manual_file}")
                continue
            
            try:
                # Extract pages from this manual
                pages_extracted = self._extract_pages(
                    pdf_path, 
                    page_numbers, 
                    pdf_writer,
                    ref['context']
                )
                
                extracted_count += pages_extracted
                extraction_log.append({
                    'manual': manual_file,
                    'pages': page_numbers,
                    'extracted': pages_extracted,
                    'context': ref['context']
                })
                
            except Exception as e:
                print(f"Error extracting from {manual_file}: {e}")
                continue
        
        # Write combined PDF if we extracted any pages
        if extracted_count > 0:
            with open(output_pdf, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Create extraction summary
            self._create_extraction_summary(output_pdf, extraction_log)
            
            print(f"\n✅ Extracted {extracted_count} pages to: {output_pdf}")
            return str(output_pdf)
        else:
            print("No pages could be extracted.")
            return ""
    
    def _parse_report_references(self, report_file: str) -> List[Dict]:
        """Parse a report file to find manual references."""
        references = []
        
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find manual references with page numbers
        # Matches: "Manual Name, Page 123" or "Manual Name - Jake, Page 456"
        pattern = r'\*\*Reference\*\*:\s*([^,]+?)(?:\s*-\s*Jake)?,\s*Page\s*(\d+)|From\s+([^*]+?)\s*\(relevance.*?Page\s*(\d+)'
        
        matches = re.findall(pattern, content)
        
        # Also look for inline page references
        inline_pattern = r'([A-Za-z\s]+Manual[^,]*?),?\s*Page\s*(\d+)'
        inline_matches = re.findall(inline_pattern, content)
        
        all_matches = []
        
        # Process matches
        for match in matches:
            if match[0] and match[1]:  # First pattern
                manual_name = match[0].strip()
                page_num = int(match[1])
                all_matches.append((manual_name, page_num))
            elif match[2] and match[3]:  # Second pattern
                manual_name = match[2].strip()
                page_num = int(match[3])
                all_matches.append((manual_name, page_num))
        
        # Add inline matches
        for manual_name, page_num in inline_matches:
            all_matches.append((manual_name.strip(), int(page_num)))
        
        # Group by manual and collect page numbers
        manual_pages = {}
        for manual_name, page_num in all_matches:
            # Try to match to actual PDF filename
            pdf_file = self._find_manual_pdf(manual_name)
            if pdf_file:
                if pdf_file not in manual_pages:
                    manual_pages[pdf_file] = {
                        'pages': set(),
                        'context': manual_name
                    }
                manual_pages[pdf_file]['pages'].add(page_num)
        
        # Convert to list format
        for pdf_file, data in manual_pages.items():
            # Add surrounding pages for context (page before and after)
            expanded_pages = set()
            for page in data['pages']:
                expanded_pages.add(page)
                if page > 1:
                    expanded_pages.add(page - 1)
                expanded_pages.add(page + 1)
            
            references.append({
                'manual_file': pdf_file,
                'pages': sorted(list(expanded_pages)),
                'context': data['context']
            })
        
        return references
    
    def _find_manual_pdf(self, manual_name: str) -> str:
        """Find the PDF file that matches the manual name."""
        # Clean up the manual name
        manual_name_lower = manual_name.lower()
        
        # Common mappings
        if "factory service manual 1991" in manual_name_lower:
            return "Factory Service Manual 1991 Toyota 4 Runner - Jake.pdf"
        elif "factory service manual 1995" in manual_name_lower:
            return "Factory Service Manual 1995 Toyota 4 Runner.pdf"
        elif "engine repair manual 3vz-e" in manual_name_lower:
            return "Engine Repair Manual 3VZ-E.pdf"
        elif "engine repair manual 5vz-fe" in manual_name_lower:
            return "Engine Repair Manual 5VZ-FE.pdf"
        elif "electrical wiring" in manual_name_lower:
            # Try to find the year
            year_match = re.search(r'(19\d{2})', manual_name)
            if year_match:
                year = year_match.group(1)
                return f"Electrical Wiring Diagram {year} Toyota 4Runner.pdf"
        
        # Try direct file matching
        for pdf_file in self.manuals_dir.glob("*.pdf"):
            if manual_name_lower in pdf_file.name.lower():
                return pdf_file.name
        
        # Fuzzy matching as last resort
        best_match = None
        best_score = 0
        
        for pdf_file in self.manuals_dir.glob("*.pdf"):
            # Simple word matching score
            score = sum(1 for word in manual_name_lower.split() 
                       if word in pdf_file.name.lower())
            if score > best_score:
                best_score = score
                best_match = pdf_file.name
        
        return best_match if best_score > 1 else None
    
    def _extract_pages(self, pdf_path: Path, page_numbers: List[int], 
                      pdf_writer: PyPDF2.PdfWriter, context: str) -> int:
        """Extract specific pages from a PDF."""
        extracted = 0
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
                
                # Add separator page
                self._add_separator_page(pdf_writer, pdf_path.name, context)
                
                for page_num in page_numbers:
                    # PyPDF2 uses 0-based indexing
                    page_index = page_num - 1
                    
                    if 0 <= page_index < total_pages:
                        page = pdf_reader.pages[page_index]
                        pdf_writer.add_page(page)
                        extracted += 1
                        print(f"  Extracted page {page_num} from {pdf_path.name}")
                    else:
                        print(f"  Warning: Page {page_num} out of range in {pdf_path.name}")
        
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        
        return extracted
    
    def _add_separator_page(self, pdf_writer: PyPDF2.PdfWriter, 
                           manual_name: str, context: str):
        """Add a separator page between different manual extracts."""
        # For now, we'll skip separator pages to keep it simple
        # In a full implementation, you could create a page with reportlab
        pass
    
    def _create_extraction_summary(self, output_pdf: Path, extraction_log: List[Dict]):
        """Create a summary text file of what was extracted."""
        summary_file = output_pdf.with_suffix('.txt')
        
        with open(summary_file, 'w') as f:
            f.write(f"PDF Page Extraction Summary\n")
            f.write(f"Output: {output_pdf.name}\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in extraction_log:
                f.write(f"Manual: {entry['manual']}\n")
                f.write(f"Context: {entry['context']}\n")
                f.write(f"Pages: {', '.join(map(str, entry['pages']))}\n")
                f.write(f"Extracted: {entry['extracted']} pages\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"Summary saved: {summary_file}")


def main():
    """Extract pages based on a report."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_page_extractor.py <report_file>")
        print("Example: python pdf_page_extractor.py reports/starting_system_diagnosis_20250605.md")
        return
    
    report_file = sys.argv[1]
    
    if not Path(report_file).exists():
        print(f"Error: Report file not found: {report_file}")
        return
    
    extractor = PDFPageExtractor()
    output_file = extractor.extract_pages_from_report(report_file)
    
    if output_file:
        print(f"\n📄 You can now print: {output_file}")
        print("This PDF contains all referenced manual pages with their diagrams and tables.")


if __name__ == "__main__":
    main()