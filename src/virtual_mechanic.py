#!/usr/bin/env python3
"""
Virtual Mechanic - ChromaDB-powered Toyota 4Runner assistance
Uses the indexed manual collection to answer specific technical questions.
"""

import logging
from typing import List, Dict, Optional
from manual_indexer import ManualIndexer
from config import VEHICLE_SPECS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VirtualMechanic:
    def __init__(self, collection_name: str = "toyota_4runner_manuals"):
        """Initialize the virtual mechanic with vehicle-specific configuration."""
        self.indexer = ManualIndexer(collection_name=collection_name)
        self.vehicle_specs = VEHICLE_SPECS
        
        # Create vehicle context string for better search filtering
        self.vehicle_context = f"{self.vehicle_specs['year']} {self.vehicle_specs['make']} {self.vehicle_specs['model']} {self.vehicle_specs['engine']} {self.vehicle_specs['transmission']}"
        
        logger.info(f"Virtual Mechanic initialized for: {self.vehicle_context}")

    def get_vehicle_info(self) -> Dict:
        """Return the current vehicle specifications."""
        return self.vehicle_specs.copy()

    def search_manuals(self, question: str, n_results: int = 5, include_context: bool = True) -> List[Dict]:
        """
        Search manuals for answers to technical questions.
        
        Args:
            question: The technical question to search for
            n_results: Number of results to return
            include_context: Whether to include vehicle context in search
            
        Returns:
            List of search results with manual references
        """
        # Enhance search query with vehicle-specific context if requested
        search_query = question
        if include_context:
            # Add vehicle-specific terms to improve search relevance
            search_query = f"{question} {self.vehicle_specs['engine']} {self.vehicle_specs['year']}"
        
        logger.info(f"Searching manuals for: '{question}'")
        logger.debug(f"Enhanced search query: '{search_query}'")
        
        # Determine if we should filter by manual type based on the question
        manual_type_filter = self._determine_manual_type(question)
        
        results = self.indexer.search_manuals(
            query=search_query,
            n_results=n_results,
            manual_type=manual_type_filter
        )
        
        # Filter results for vehicle-specific relevance
        filtered_results = self._filter_for_vehicle_relevance(results, question)
        
        return filtered_results

    def _determine_manual_type(self, question: str) -> Optional[str]:
        """Determine the most relevant manual type based on the question."""
        question_lower = question.lower()
        
        if any(term in question_lower for term in ['wiring', 'electrical', 'circuit', 'fuse', 'relay']):
            return 'electrical_diagram'
        elif any(term in question_lower for term in ['engine', 'timing', 'belt', 'oil', 'coolant', 'carburetor']):
            return 'engine_repair_manual'
        elif any(term in question_lower for term in ['service', 'maintenance', 'repair', 'factory']):
            return 'factory_service_manual'
        else:
            return None  # Search all manual types

    def _filter_for_vehicle_relevance(self, results: List[Dict], question: str) -> List[Dict]:
        """Filter and rank results based on vehicle-specific relevance."""
        if not results:
            return results
        
        # Create relevance scoring based on vehicle specs
        vehicle_keywords = [
            self.vehicle_specs['engine'].lower(),
            str(self.vehicle_specs['year']),
            self.vehicle_specs['transmission'].lower(),
            'manual transmission' if 'manual' in self.vehicle_specs['transmission'].lower() else 'automatic',
            '4wd' if '4x4' in self.vehicle_specs['drive_type'].lower() else '2wd',
            '3vz-e',  # Specific engine code
            'n60'     # Series code
        ]
        
        # Score each result
        for result in results:
            content_lower = result['content'].lower()
            metadata = result.get('metadata', {})
            
            relevance_score = result['similarity_score']
            
            # Boost score for vehicle-specific matches
            for keyword in vehicle_keywords:
                if keyword in content_lower:
                    relevance_score += 0.1
            
            # Boost score for year matches in metadata
            if metadata.get('year') == str(self.vehicle_specs['year']):
                relevance_score += 0.15
            
            # Boost score for engine matches in metadata
            if metadata.get('engine') and '3vz-e' in metadata.get('engine', '').lower():
                relevance_score += 0.2
            
            result['vehicle_relevance_score'] = relevance_score
        
        # Re-sort by vehicle relevance score
        results.sort(key=lambda x: x['vehicle_relevance_score'], reverse=True)
        
        return results

    def ask_question(self, question: str, n_results: int = 3) -> str:
        """
        Ask a technical question and get a formatted response with manual references.
        
        Args:
            question: The technical question
            n_results: Number of manual references to include
            
        Returns:
            Formatted response with answer and manual references
        """
        results = self.search_manuals(question, n_results=n_results)
        
        if not results:
            return f"I couldn't find specific information about '{question}' in your manuals. Try rephrasing the question or checking if it's covered in a different section."
        
        # Format the response
        response = f"**Question**: {question}\n\n"
        response += f"**Vehicle**: {self.vehicle_context}\n\n"
        response += "**Answer from manuals**:\n\n"
        
        for i, result in enumerate(results, 1):
            manual_name = result['manual']
            content = result['content']
            score = result.get('vehicle_relevance_score', result['similarity_score'])
            
            # Clean up the content for better readability
            clean_content = content.replace('---', '').strip()
            if len(clean_content) > 300:
                clean_content = clean_content[:300] + "..."
            
            response += f"**{i}. From {manual_name}** (relevance: {score:.3f})\n"
            response += f"{clean_content}\n\n"
        
        response += "---\n"
        response += f"*Based on {len(results)} manual references for your {self.vehicle_context}*"
        
        return response

    def get_manual_coverage(self) -> Dict:
        """Get information about what manuals are available for this vehicle."""
        stats = self.indexer.get_collection_stats()
        
        coverage = {
            "total_chunks": stats.get('total_chunks', 0),
            "manual_types": stats.get('manual_types', {}),
            "years_covered": stats.get('years', {}),
            "engines_covered": stats.get('engines', {}),
            "vehicle_match": False
        }
        
        # Check if we have specific coverage for this vehicle
        vehicle_year = str(self.vehicle_specs['year'])
        if vehicle_year in coverage['years_covered']:
            coverage['vehicle_match'] = True
        
        return coverage


def main():
    """Test the virtual mechanic functionality."""
    mechanic = VirtualMechanic()
    
    print("Virtual Mechanic for Toyota 4Runner")
    print("=" * 50)
    
    # Show vehicle info
    vehicle_info = mechanic.get_vehicle_info()
    print(f"Vehicle: {vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']}")
    print(f"Engine: {vehicle_info['engine']}")
    print(f"Transmission: {vehicle_info['transmission']}")
    print(f"Drive Type: {vehicle_info['drive_type']}")
    print()
    
    # Show manual coverage
    coverage = mechanic.get_manual_coverage()
    print(f"Manual Coverage: {coverage['total_chunks']} indexed sections")
    print(f"Vehicle-specific data available: {'Yes' if coverage['vehicle_match'] else 'No'}")
    print()
    
    # Test some questions
    test_questions = [
        "How do I change the timing belt?",
        "What is the transmission fluid capacity?",
        "How do I adjust the carburetor idle speed?",
        "What are the torque specifications for the engine bolts?"
    ]
    
    for question in test_questions:
        print("=" * 50)
        print(mechanic.ask_question(question))
        print()


if __name__ == "__main__":
    main()