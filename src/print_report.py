#!/usr/bin/env python3
"""
Print Report - Convert markdown reports to formatted printable documents
"""

import os
import sys
import subprocess
from pathlib import Path
import tempfile

def print_markdown_report(md_file_path: str, method: str = "auto"):
    """
    Print a markdown report with formatting.
    
    Methods:
    - pandoc: Uses pandoc to convert MD to PDF (best quality)
    - wkhtmltopdf: Uses wkhtmltopdf for HTML to PDF
    - grip: Uses grip to create HTML then print
    - enscript: Quick text-based printing
    """
    
    file_path = Path(md_file_path)
    if not file_path.exists():
        print(f"Error: File {md_file_path} not found!")
        return False
    
    # Check available tools and auto-select method
    if method == "auto":
        if check_command_exists("pandoc"):
            method = "pandoc"
        elif check_command_exists("wkhtmltopdf"):
            method = "wkhtmltopdf"
        elif check_command_exists("grip"):
            method = "grip"
        else:
            method = "enscript"
    
    print(f"Using {method} method for printing...")
    
    if method == "pandoc":
        return print_with_pandoc(file_path)
    elif method == "wkhtmltopdf":
        return print_with_wkhtmltopdf(file_path)
    elif method == "grip":
        return print_with_grip(file_path)
    else:
        return print_with_enscript(file_path)

def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system."""
    try:
        subprocess.run(['which', command], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def print_with_pandoc(file_path: Path) -> bool:
    """Use pandoc to convert MD to PDF and print."""
    try:
        # First check if pandoc is installed
        if not check_command_exists("pandoc"):
            print("Installing pandoc... (this may take a moment)")
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'pandoc'], check=True)
        
        # Convert to PDF
        pdf_path = file_path.with_suffix('.pdf')
        print(f"Converting {file_path.name} to PDF...")
        
        # Create custom LaTeX template for better formatting
        template_content = """
\\documentclass[11pt]{article}
\\usepackage[margin=1in]{geometry}
\\usepackage{fancyhdr}
\\usepackage{listings}
\\usepackage{xcolor}
\\usepackage{hyperref}

\\pagestyle{fancy}
\\fancyhf{}
\\fancyhead[L]{Toyota 4Runner Virtual Mechanic Report}
\\fancyhead[R]{\\thepage}

\\lstset{
    basicstyle=\\ttfamily\\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\\color{gray!10}
}

\\begin{document}
$body$
\\end{document}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as template:
            template.write(template_content)
            template_path = template.name
        
        # Run pandoc
        subprocess.run([
            'pandoc', str(file_path),
            '-o', str(pdf_path),
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=1in',
            '-V', 'fontsize=11pt',
            '-V', 'colorlinks=true'
        ], check=True)
        
        # Print the PDF
        print(f"Sending {pdf_path.name} to printer...")
        subprocess.run(['lp', str(pdf_path)], check=True)
        
        # Clean up
        os.unlink(template_path)
        
        print(f"✅ Successfully printed {file_path.name}")
        print(f"📄 PDF saved as: {pdf_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error with pandoc: {e}")
        return False

def print_with_wkhtmltopdf(file_path: Path) -> bool:
    """Use wkhtmltopdf to convert MD to PDF via HTML."""
    try:
        # Check if wkhtmltopdf is installed
        if not check_command_exists("wkhtmltopdf"):
            print("Installing wkhtmltopdf...")
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'wkhtmltopdf'], check=True)
        
        # First convert MD to HTML using grip
        html_path = file_path.with_suffix('.html')
        pdf_path = file_path.with_suffix('.pdf')
        
        print(f"Converting {file_path.name} to HTML...")
        
        # Use grip to export HTML
        subprocess.run([
            'grip', str(file_path), '--export', str(html_path)
        ], check=True)
        
        # Convert HTML to PDF
        print(f"Converting HTML to PDF...")
        subprocess.run([
            'wkhtmltopdf',
            '--enable-local-file-access',
            '--margin-top', '20mm',
            '--margin-bottom', '20mm',
            '--margin-left', '20mm',
            '--margin-right', '20mm',
            str(html_path),
            str(pdf_path)
        ], check=True)
        
        # Print the PDF
        print(f"Sending {pdf_path.name} to printer...")
        subprocess.run(['lp', str(pdf_path)], check=True)
        
        # Clean up
        os.unlink(html_path)
        
        print(f"✅ Successfully printed {file_path.name}")
        print(f"📄 PDF saved as: {pdf_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error with wkhtmltopdf: {e}")
        return False

def print_with_grip(file_path: Path) -> bool:
    """Use grip to create HTML and print directly."""
    try:
        # Export to HTML
        html_path = file_path.with_suffix('.html')
        
        print(f"Converting {file_path.name} to HTML...")
        subprocess.run([
            'grip', str(file_path), '--export', str(html_path)
        ], check=True)
        
        # Add print-friendly CSS
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        # Inject print CSS - Remove borders and use full page width
        print_css = """
        <style type="text/css">
            /* Remove GitHub container styling */
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 100% !important;
                margin: 0 !important;
                padding: 20px !important;
                border: none !important;
                box-shadow: none !important;
            }
            
            .container-lg {
                max-width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* Remove all borders from the main container */
            #readme, .Box, .Box-body {
                border: none !important;
                box-shadow: none !important;
                margin: 0 !important;
            }
            
            /* Print-specific styles */
            @media print {
                @page { 
                    size: letter;
                    margin: 0.5in;
                }
                
                body {
                    font-size: 11pt;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                
                .markdown-body {
                    padding: 0 !important;
                }
                
                /* Better code block printing - prevent overflow */
                pre {
                    page-break-inside: avoid;
                    border: 1px solid #ddd !important;
                    background-color: #f6f8fa !important;
                    white-space: pre-wrap !important;
                    word-wrap: break-word !important;
                    overflow-wrap: break-word !important;
                    max-width: 100% !important;
                }
                
                code {
                    white-space: pre-wrap !important;
                    word-break: break-word !important;
                }
                
                /* Prevent headers from being orphaned */
                h1, h2, h3, h4 { 
                    page-break-after: avoid;
                    margin-top: 20px;
                }
                
                /* Hide navigation and other GitHub UI elements */
                .Header, .footer, nav, .js-header-wrapper {
                    display: none !important;
                }
                
                /* Ensure tables fit on page */
                table {
                    font-size: 10pt;
                    width: 100% !important;
                }
                
                /* Improve list formatting */
                ul, ol {
                    margin-left: 20px;
                }
            }
            
            /* Screen styles - also remove borders */
            @media screen {
                body {
                    background: white !important;
                }
                
                .markdown-body {
                    border: none !important;
                    box-shadow: none !important;
                }
            }
        </style>
        """
        
        html_content = html_content.replace('</head>', print_css + '</head>')
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Open in browser for printing (most reliable)
        print(f"Opening {html_path.name} in browser for printing...")
        subprocess.run(['xdg-open', str(html_path)], check=True)
        
        print(f"✅ HTML file opened in browser")
        print("📄 Use browser's Print function (Ctrl+P) to print with formatting")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error with grip: {e}")
        return False

def print_with_enscript(file_path: Path) -> bool:
    """Basic text printing with enscript."""
    try:
        # Check if enscript is installed
        if not check_command_exists("enscript"):
            print("Installing enscript...")
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'enscript'], check=True)
        
        print(f"Printing {file_path.name} as formatted text...")
        
        # Print with enscript
        subprocess.run([
            'enscript',
            '--fancy-header',
            '--word-wrap',
            '--media=Letter',
            '-p', '-',  # Output to stdout
            str(file_path)
        ], stdout=subprocess.PIPE, check=True)
        
        print(f"✅ Successfully sent {file_path.name} to printer")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error with enscript: {e}")
        return False

def list_reports():
    """List all available reports."""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        print("No reports directory found!")
        return
    
    print("\n📄 Available Reports:")
    print("=" * 50)
    
    md_files = list(reports_dir.glob("*.md"))
    if not md_files:
        print("No markdown reports found!")
        return
    
    for i, file in enumerate(md_files, 1):
        size = file.stat().st_size / 1024  # KB
        print(f"{i}. {file.name} ({size:.1f} KB)")
    
    return md_files

def main():
    """Command line interface for printing reports."""
    if len(sys.argv) < 2:
        # List available reports
        md_files = list_reports()
        if md_files:
            print("\nUsage:")
            print("  python print_report.py <report_file>")
            print("  python print_report.py <number>")
            print("  python print_report.py <number> --with-pages  # Also extract PDF pages")
            print("\nExample:")
            print("  python print_report.py reports/starting_system_diagnosis_20250605.md")
            print("  python print_report.py 1")
            print("  python print_report.py 1 --with-pages")
        return
    
    report_arg = sys.argv[1]
    
    # Check if it's a number (select from list)
    try:
        report_num = int(report_arg)
        md_files = list(Path("reports").glob("*.md"))
        if 1 <= report_num <= len(md_files):
            report_file = str(md_files[report_num - 1])
        else:
            print(f"Invalid number. Choose between 1 and {len(md_files)}")
            return
    except ValueError:
        report_file = report_arg
    
    # Check for flags
    extract_pages = "--with-pages" in sys.argv
    method = "auto"
    
    # Find method if specified (not a flag)
    for arg in sys.argv[2:]:
        if not arg.startswith("--"):
            method = arg
            break
    
    print(f"\n🖨️ Preparing to print: {Path(report_file).name}")
    
    # Extract PDF pages if requested
    if extract_pages:
        print("\n📚 Also extracting referenced PDF pages...")
        try:
            from extract_manual_pages import extract_with_preview
            extract_with_preview(report_file)
        except ImportError:
            print("PDF page extraction not available (missing dependencies)")
        except Exception as e:
            print(f"Error extracting PDF pages: {e}")
        print()
    
    print_markdown_report(report_file, method)

if __name__ == "__main__":
    main()