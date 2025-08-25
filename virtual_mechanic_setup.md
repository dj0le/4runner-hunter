# 4Runner Virtual Mechanic Setup with ChromaDB MCP

## Overview
Create an AI-powered virtual mechanic that can answer questions about Toyota 4Runner maintenance and repair using your PDF manuals.

## Architecture

### 1. ChromaDB Setup
```json
// Add to .mcp.json
"chromadb": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-chromadb"],
  "env": {
    "CHROMADB_PATH": "./4runner_mechanic_db"
  }
}
```

### 2. PDF Processing Script
Create `process_manuals.py`:

```python
import os
import chromadb
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./4runner_mechanic_db")

# Create collections for different manual types
collections = {
    "maintenance": client.get_or_create_collection("4runner_maintenance"),
    "repair": client.get_or_create_collection("4runner_repair"),
    "specs": client.get_or_create_collection("4runner_specifications"),
    "troubleshooting": client.get_or_create_collection("4runner_troubleshooting")
}

def process_pdf(pdf_path, collection_name, vehicle_info):
    """Process a PDF and add to ChromaDB collection"""
    
    # Read PDF
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    
    # Add to ChromaDB
    collection = collections[collection_name]
    
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            metadatas=[{
                "source": pdf_path,
                "page": i,
                "year_range": vehicle_info["years"],
                "generation": vehicle_info["gen"],
                "type": collection_name
            }],
            ids=[f"{os.path.basename(pdf_path)}_chunk_{i}"]
        )

# Process your manuals
manuals = [
    {
        "path": "manuals/1984-1989_4Runner_Service_Manual.pdf",
        "collection": "repair",
        "info": {"years": "1984-1989", "gen": "1st"}
    },
    {
        "path": "manuals/1996-2002_4Runner_Repair_Manual.pdf",
        "collection": "repair", 
        "info": {"years": "1996-2002", "gen": "3rd"}
    },
    # Add more manuals...
]

for manual in manuals:
    process_pdf(manual["path"], manual["collection"], manual["info"])
```

### 3. Usage in Claude Code

Once set up, you can ask questions like:

```bash
# Specific repair procedures
"How do I replace the timing belt on a 1997 4Runner?"
"What's the procedure for bleeding the clutch on a manual 4Runner?"

# Torque specifications
"What are the head bolt torque specs for a 3VZ-E engine?"
"Wheel lug nut torque for 2000 4Runner?"

# Troubleshooting
"My 4Runner won't start when cold, what should I check?"
"Transfer case is making grinding noise in 4WD"

# Maintenance schedules
"What's the service interval for differential fluid?"
"When should I change the timing belt on a 1999 4Runner?"
```

### 4. Enhanced Queries with Metadata

The ChromaDB MCP will search based on:
- Semantic similarity to your question
- Filter by year/generation if specified
- Return relevant manual sections with source info

### 5. Integration with 4Runner Hunter

Add a section to your web app:
```python
# In web_app.py
@app.route('/mechanic')
def virtual_mechanic():
    return render_template('mechanic.html')

# Query ChromaDB through the MCP in Claude Code
# Return answers to the web interface
```

## Benefits Over Separate RAG Project

1. **Integrated with your existing 4Runner Hunter project**
2. **No separate infrastructure to maintain**
3. **Can combine with vehicle listing data** (e.g., "Common issues with 1997 manual 4Runners in the listings?")
4. **Easy to update** - just add new PDFs and reprocess
5. **Natural language interface** through Claude Code

## Next Steps

1. Add ChromaDB to your .mcp.json
2. Create a `manuals/` directory in your project
3. Add your PDF manuals
4. Run the processing script
5. Start asking questions!

Would you like me to help set this up?