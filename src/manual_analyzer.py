#!/usr/bin/env python3
"""
Manual Analyzer - Analyzes indexed manuals and creates manual-specific metadata
"""

import json
from pathlib import Path
from typing import Dict, List
from manual_indexer import ManualIndexer

class ManualAnalyzer:
    def __init__(self, collection_name: str = "toyota_4runner_manuals"):
        """Initialize manual analyzer."""
        self.indexer = ManualIndexer(collection_name=collection_name)
        
    def analyze_manual_coverage(self) -> Dict:
        """Analyze what each manual covers and create summaries."""
        try:
            # Get all documents grouped by manual
            all_docs = self.indexer.collection.get(include=["documents", "metadatas"])
            
            manual_analysis = {}
            
            # Group by manual filename
            for doc, metadata in zip(all_docs["documents"], all_docs["metadatas"]):
                filename = metadata.get("filename", "Unknown")
                
                if filename not in manual_analysis:
                    manual_analysis[filename] = {
                        "metadata": {
                            "filename": filename,
                            "manual_type": metadata.get("manual_type", "unknown"),
                            "year": metadata.get("year", "unknown"),
                            "engine": metadata.get("engine", "unknown"),
                            "file_path": metadata.get("file_path", "unknown")
                        },
                        "total_chunks": 0,
                        "content_keywords": {},
                        "topics": set(),
                        "sample_content": []
                    }
                
                analysis = manual_analysis[filename]
                analysis["total_chunks"] += 1
                
                # Analyze content for keywords
                doc_lower = doc.lower()
                
                # Track automotive keywords
                keywords = {
                    "engine": ["engine", "cylinder", "piston", "valve", "timing", "camshaft", "crankshaft"],
                    "transmission": ["transmission", "clutch", "gear", "shift", "manual", "automatic"],
                    "electrical": ["electrical", "wiring", "circuit", "fuse", "relay", "connector"],
                    "brake": ["brake", "pad", "disc", "rotor", "caliper", "master cylinder"],
                    "cooling": ["cooling", "radiator", "thermostat", "coolant", "water pump"],
                    "fuel": ["fuel", "carburetor", "injection", "pump", "filter", "tank"],
                    "suspension": ["suspension", "shock", "strut", "spring", "control arm"],
                    "steering": ["steering", "power steering", "rack", "pinion", "wheel"],
                    "maintenance": ["oil", "filter", "service", "maintenance", "replace", "inspect"],
                    "4wd": ["4wd", "transfer", "differential", "axle", "4x4", "front", "rear"],
                    "troubleshooting": ["troubleshoot", "diagnosis", "problem", "symptom", "check"]
                }
                
                for topic, topic_keywords in keywords.items():
                    for keyword in topic_keywords:
                        if keyword in doc_lower:
                            analysis["content_keywords"][topic] = analysis["content_keywords"].get(topic, 0) + 1
                            analysis["topics"].add(topic)
                
                # Store sample content (first few interesting chunks)
                if len(analysis["sample_content"]) < 3 and len(doc.strip()) > 50:
                    clean_doc = doc.replace("---", "").strip()
                    if clean_doc and not clean_doc.startswith("Page"):
                        analysis["sample_content"].append(clean_doc[:200] + "...")
            
            # Convert sets to lists for JSON serialization
            for manual in manual_analysis.values():
                manual["topics"] = list(manual["topics"])
                
            return manual_analysis
            
        except Exception as e:
            print(f"Error analyzing manuals: {e}")
            return {}
    
    def generate_manual_summaries(self, output_dir: str = "manual_summaries") -> Dict[str, str]:
        """Generate individual manual summary files (like CLAUDE.md for each manual)."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        analysis = self.analyze_manual_coverage()
        summary_files = {}
        
        for filename, data in analysis.items():
            # Create safe filename
            safe_filename = filename.replace(" ", "_").replace(".pdf", "").replace("-", "_")
            summary_file = output_path / f"{safe_filename}_SUMMARY.md"
            
            # Generate summary content
            metadata = data["metadata"]
            topics = data["topics"]
            keywords = data["content_keywords"]
            
            summary_content = f"""# {filename} - Manual Summary

## Manual Information
- **File**: {filename}
- **Type**: {metadata['manual_type'].replace('_', ' ').title()}
- **Year**: {metadata.get('year', 'Unknown')}
- **Engine**: {metadata.get('engine', 'Unknown')}
- **Total Sections**: {data['total_chunks']}

## Topics Covered
{', '.join(sorted(topics)) if topics else 'No specific topics identified'}

## Content Analysis
"""
            
            # Add keyword frequency analysis
            if keywords:
                summary_content += "\n### Keyword Frequency\n"
                sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                for topic, count in sorted_keywords[:10]:  # Top 10
                    summary_content += f"- **{topic.title()}**: {count} mentions\n"
            
            # Add sample content
            if data["sample_content"]:
                summary_content += "\n### Sample Content\n"
                for i, sample in enumerate(data["sample_content"], 1):
                    summary_content += f"\n**Sample {i}:**\n```\n{sample}\n```\n"
            
            # Add usage recommendations
            summary_content += f"""
## Best Used For
"""
            
            # Recommend usage based on content analysis
            recommendations = []
            
            if "engine" in topics and keywords.get("engine", 0) > 10:
                recommendations.append("Engine repair and maintenance procedures")
            if "electrical" in topics and keywords.get("electrical", 0) > 5:
                recommendations.append("Electrical system troubleshooting and wiring diagrams")
            if "transmission" in topics:
                recommendations.append("Transmission service and repair")
            if "4wd" in topics:
                recommendations.append("4WD system maintenance and transfer case service")
            if "maintenance" in topics and keywords.get("maintenance", 0) > 5:
                recommendations.append("General maintenance procedures and specifications")
            if "troubleshooting" in topics:
                recommendations.append("Diagnostic procedures and problem solving")
            
            if recommendations:
                for rec in recommendations:
                    summary_content += f"- {rec}\n"
            else:
                summary_content += "- General reference (content analysis incomplete)\n"
            
            summary_content += f"""
## Search Efficiency
- **High relevance for**: {', '.join(list(topics)[:5]) if topics else 'General queries'}
- **Content density**: {data['total_chunks']} searchable sections
- **Manual type**: {metadata['manual_type'].replace('_', ' ').title()}

---
*Generated by Manual Analyzer - {Path(__file__).name}*
"""
            
            # Write summary file
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            summary_files[filename] = str(summary_file)
        
        return summary_files
    
    def create_master_manual_index(self, output_file: str = "MANUAL_INDEX.md") -> str:
        """Create a master index of all manuals with their capabilities."""
        analysis = self.analyze_manual_coverage()
        
        content = f"""# Toyota 4Runner Manual Index

**Generated**: {Path(__file__).name}
**Total Manuals**: {len(analysis)}

## Quick Reference Guide

This index helps you quickly identify which manual to search for specific topics.

"""
        
        # Group by manual type
        by_type = {}
        for filename, data in analysis.items():
            manual_type = data["metadata"]["manual_type"]
            if manual_type not in by_type:
                by_type[manual_type] = []
            by_type[manual_type].append((filename, data))
        
        for manual_type, manuals in by_type.items():
            content += f"\n## {manual_type.replace('_', ' ').title()}\n\n"
            
            for filename, data in manuals:
                topics = data["topics"]
                chunks = data["total_chunks"]
                year = data["metadata"].get("year", "Unknown")
                engine = data["metadata"].get("engine", "Unknown")
                
                content += f"### {filename}\n"
                content += f"- **Year**: {year}\n"
                content += f"- **Engine**: {engine}\n" 
                content += f"- **Sections**: {chunks}\n"
                content += f"- **Topics**: {', '.join(sorted(topics)[:8]) if topics else 'General'}\n"
                content += f"- **Best for**: "
                
                # Quick recommendations
                if "electrical" in topics:
                    content += "Wiring diagrams, electrical troubleshooting"
                elif "engine" in topics and chunks > 50:
                    content += "Engine repair, timing, maintenance procedures"
                elif "maintenance" in topics:
                    content += "Service procedures, fluid specifications"
                else:
                    content += "General reference"
                
                content += "\n\n"
        
        # Add topic cross-reference
        content += "\n## Topic Cross-Reference\n\n"
        content += "| Topic | Available in Manuals |\n"
        content += "|-------|---------------------|\n"
        
        all_topics = set()
        for data in analysis.values():
            all_topics.update(data["topics"])
        
        for topic in sorted(all_topics):
            manuals_with_topic = []
            for filename, data in analysis.items():
                if topic in data["topics"]:
                    short_name = filename.replace(" Toyota 4 Runner", "").replace(".pdf", "")
                    manuals_with_topic.append(short_name)
            
            content += f"| {topic.title()} | {', '.join(manuals_with_topic[:3])}{'...' if len(manuals_with_topic) > 3 else ''} |\n"
        
        content += f"""
## Search Strategy Tips

1. **Engine Issues**: Start with "Engine Repair Manual 3VZ-E" 
2. **Electrical Problems**: Use "Electrical Wiring Diagram" manuals
3. **Service Procedures**: Check "Factory Service Manual" for your year
4. **Transmission Issues**: Look for "R150f Service Manual" or Factory Service manuals
5. **General Maintenance**: Factory Service manuals have comprehensive procedures

---
*Total indexed content: {sum(data['total_chunks'] for data in analysis.values())} searchable sections*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file


def main():
    """Analyze manuals and generate summaries."""
    analyzer = ManualAnalyzer()
    
    print("Toyota 4Runner Manual Analyzer")
    print("=" * 40)
    
    # Analyze manual coverage
    print("Analyzing manual coverage...")
    analysis = analyzer.analyze_manual_coverage()
    
    print(f"Found {len(analysis)} manuals in collection:")
    for filename, data in analysis.items():
        topics = len(data["topics"])
        chunks = data["total_chunks"]
        print(f"  • {filename}: {chunks} sections, {topics} topics")
    
    # Generate individual manual summaries
    print("\nGenerating manual summaries...")
    summary_files = analyzer.generate_manual_summaries()
    
    for manual, summary_file in summary_files.items():
        print(f"  ✅ {summary_file}")
    
    # Create master index
    print("\nCreating master manual index...")
    index_file = analyzer.create_master_manual_index()
    print(f"  ✅ {index_file}")
    
    print(f"\nAnalysis complete! Check the generated files for manual insights.")


if __name__ == "__main__":
    main()