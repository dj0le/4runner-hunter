#!/usr/bin/env python3
"""
Toyota 4Runner Manual Indexer - ChromaDB Integration
Extracts text from PDF manuals and indexes them for the virtual mechanic system.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not found. Installing...")
    os.system(f"{sys.executable} -m pip install PyPDF2")
    import PyPDF2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualIndexer:
    def __init__(self, manuals_dir: str = None, collection_name: str = "toyota_4runner_manuals"):
        """Initialize the manual indexer with ChromaDB connection."""
        if manuals_dir is None:
            # Default to manuals directory in project root
            project_root = Path(__file__).parent.parent
            self.manuals_dir = project_root / "manuals"
        else:
            self.manuals_dir = Path(manuals_dir)
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient()
        
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Connected to existing collection: {collection_name}")
        except Exception:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Toyota 4Runner service manuals and repair documentation"}
            )
            logger.info(f"Created new collection: {collection_name}")

    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1} from {pdf_path.name}: {e}")
                        continue
                
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path.name}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better search results."""
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks

    def extract_manual_metadata(self, pdf_path: Path) -> Dict[str, str]:
        """Extract metadata from manual filename and content."""
        filename = pdf_path.stem
        metadata = {
            "filename": filename,
            "file_path": str(pdf_path),
            "manual_type": "unknown"
        }
        
        # Parse filename for metadata
        filename_lower = filename.lower()
        
        # Determine manual type
        if "factory service manual" in filename_lower:
            metadata["manual_type"] = "factory_service_manual"
        elif "engine repair" in filename_lower:
            metadata["manual_type"] = "engine_repair_manual"
        elif "electrical wiring" in filename_lower:
            metadata["manual_type"] = "electrical_diagram"
        elif "haynes" in filename_lower:
            metadata["manual_type"] = "haynes_manual"
        elif "aisin" in filename_lower:
            metadata["manual_type"] = "component_manual"
        elif "maintenance" in filename_lower:
            metadata["manual_type"] = "maintenance_guide"
        
        # Extract year information
        import re
        year_match = re.search(r'(19\d{2}|20\d{2})', filename)
        if year_match:
            metadata["year"] = year_match.group(1)
        
        # Extract engine information
        engine_match = re.search(r'(3VZ-E|3VZ-FE|5VZ-FE|R150f)', filename_lower)
        if engine_match:
            metadata["engine"] = engine_match.group(1).upper()
        
        return metadata

    def index_manual(self, pdf_path: Path) -> bool:
        """Index a single manual into ChromaDB."""
        logger.info(f"Indexing manual: {pdf_path.name}")
        
        # Extract text from PDF
        text = self.extract_pdf_text(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path.name}")
            return False
        
        # Extract metadata
        metadata = self.extract_manual_metadata(pdf_path)
        
        # Chunk the text
        chunks = self.chunk_text(text)
        if not chunks:
            logger.warning(f"No text chunks created for {pdf_path.name}")
            return False
        
        # Prepare documents for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{pdf_path.stem}_chunk_{i:04d}"
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "text_length": len(chunk)
            })
            
            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(chunk_id)
        
        # Add to ChromaDB
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully indexed {len(chunks)} chunks from {pdf_path.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB for {pdf_path.name}: {e}")
            return False

    def index_all_manuals(self) -> Dict[str, bool]:
        """Index all PDF manuals in the manuals directory."""
        if not self.manuals_dir.exists():
            logger.error(f"Manuals directory not found: {self.manuals_dir}")
            return {}
        
        pdf_files = list(self.manuals_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.manuals_dir}")
            return {}
        
        logger.info(f"Found {len(pdf_files)} PDF files to index")
        
        results = {}
        for pdf_path in pdf_files:
            try:
                results[pdf_path.name] = self.index_manual(pdf_path)
            except Exception as e:
                logger.error(f"Error indexing {pdf_path.name}: {e}")
                results[pdf_path.name] = False
        
        return results

    def search_manuals(self, query: str, n_results: int = 5, manual_type: str = None) -> List[Dict]:
        """Search the indexed manuals."""
        where_filter = {}
        if manual_type:
            where_filter["manual_type"] = manual_type
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0], 
                results["distances"][0]
            )):
                search_results.append({
                    "rank": i + 1,
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Convert distance to similarity
                    "manual": metadata.get("filename", "Unknown"),
                    "manual_type": metadata.get("manual_type", "unknown"),
                    "year": metadata.get("year", "Unknown")
                })
            
            return search_results
        except Exception as e:
            logger.error(f"Error searching manuals: {e}")
            return []

    def get_collection_stats(self) -> Dict:
        """Get statistics about the indexed collection."""
        try:
            count = self.collection.count()
            
            # Get sample documents to analyze
            sample = self.collection.get(limit=min(100, count), include=["metadatas"])
            
            stats = {
                "total_chunks": count,
                "manual_types": {},
                "years": {},
                "engines": {}
            }
            
            for metadata in sample["metadatas"]:
                # Count manual types
                manual_type = metadata.get("manual_type", "unknown")
                stats["manual_types"][manual_type] = stats["manual_types"].get(manual_type, 0) + 1
                
                # Count years
                year = metadata.get("year", "unknown")
                stats["years"][year] = stats["years"].get(year, 0) + 1
                
                # Count engines
                engine = metadata.get("engine", "unknown")
                stats["engines"][engine] = stats["engines"].get(engine, 0) + 1
            
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}


def main():
    """Main function to run the indexer."""
    indexer = ManualIndexer()
    
    print("Toyota 4Runner Manual Indexer")
    print("=" * 40)
    
    # Index all manuals
    print("Starting indexing process...")
    results = indexer.index_all_manuals()
    
    # Display results
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\nIndexing Results:")
    print(f"Successfully indexed: {successful}/{total} manuals")
    
    for filename, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {filename}")
    
    # Show collection stats
    print("\nCollection Statistics:")
    stats = indexer.get_collection_stats()
    print(f"Total text chunks: {stats.get('total_chunks', 0)}")
    
    if stats.get('manual_types'):
        print("\nManual Types:")
        for manual_type, count in stats['manual_types'].items():
            print(f"  {manual_type}: {count} chunks")
    
    if stats.get('years'):
        print("\nYears Covered:")
        for year, count in sorted(stats['years'].items()):
            print(f"  {year}: {count} chunks")
    
    # Test search functionality
    print("\n" + "=" * 40)
    print("Testing search functionality...")
    
    test_queries = [
        "transmission oil change",
        "engine timing belt",
        "electrical wiring diagram",
        "brake system maintenance"
    ]
    
    for query in test_queries:
        print(f"\nSearch: '{query}'")
        results = indexer.search_manuals(query, n_results=3)
        for result in results:
            print(f"  {result['rank']}. {result['manual']} ({result['similarity_score']:.3f})")
            print(f"     {result['content'][:100]}...")


if __name__ == "__main__":
    main()