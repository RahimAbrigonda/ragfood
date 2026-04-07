# 🏠 Local Version Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- At least 5GB free disk space
- 4GB+ RAM
- Decent CPU (local LLM inference can be slow)

## Step 1: Install Ollama

### Windows

1. Download from https://ollama.ai/download
2. Run the installer
3. Wait for installation to complete
4. Open PowerShell and verify:

```bash
ollama --version
# Output: ollama version X.X.X
```

### macOS

```bash
# Using Homebrew
brew install ollama

# Or download from https://ollama.ai/download
```

### Linux

```bash
curl https://ollama.ai/install.sh | sh
```

## Step 2: Pull Required Models

```bash
# Start Ollama service (this runs in background)
ollama serve

# In another terminal, pull the models
ollama pull mxbai-embed-large    # For embeddings (1GB)
ollama pull llama3.2              # For LLM responses (4GB)

# Verify models are installed
ollama list
```

**Expected output:**
```
NAME                    ID              SIZE      MODIFIED
mxbai-embed-large      abc123...       273 MB    2 minutes ago
llama3.2               def456...       4.0 GB    1 minute ago
```

> **Note**: This downloads ~4.3GB of model files. May take 5-10 minutes on fast internet.

## Step 3: Clone Repository

```bash
# Clone the repository
git clone https://github.com/gocallum/ragfood.git
cd ragfood

# Checkout cloud-migration branch
git checkout cloud-migration
```

## Step 4: Create Virtual Environment

```bash
# On Windows
python -m venv ENV
.\ENV\Scripts\activate

# On macOS/Linux
python3 -m venv ENV
source ENV/bin/activate
```

## Step 5: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep chromadb
```

## Step 6: Start Ollama Service

Open a **new terminal window** and start Ollama:

```bash
ollama serve
```

Wait until you see:
```
Loaded weights from /path/to/models
Listening on 127.0.0.1:11434
```

**Keep this window open** - Ollama needs to stay running while you use RAG-Food.

## Step 7: Run Local Version

In your **first terminal** (where virtual environment is active):

```bash
# Navigate to local version directory
cd local-version

# Run the application
python rag_run_local.py
```

### Expected Output

```
🆕 Adding 110 new documents to Chroma...
✅ All documents already in ChromaDB.

🧠 RAG is ready. Ask a question (type 'exit' to quit):

You: 
```

## Step 8: Test with Queries

```bash
# Example 1: Health-conscious foods
You: What are healthy mediterranean options?

# Example 2: Indian cuisine
You: Which Indian dishes use chickpeas?

# Example 3: Nutritional query
You: Show me high-protein breakfast options?

# Exit
You: exit
```

## Troubleshooting

### Issue: "Connection refused" on localhost:11434

**Cause**: Ollama service not running

**Solution**:
1. Open new terminal window
2. Run `ollama serve`
3. Wait for "Listening on 127.0.0.1:11434" message
4. Keep it running in background

### Issue: "Failed to pull model"

**Cause**: Network issue or disk space

**Solution**:
```bash
# Check disk space
df -h  # macOS/Linux
Get-Volume  # Windows PowerShell

# Try pulling again with retry
ollama pull mxbai-embed-large
```

### Issue: "Out of memory"

**Cause**: System doesn't have enough RAM

**Solution**:
1. Close unnecessary applications
2. Check available RAM: `free -h` (Linux) or Task Manager (Windows)
3. Consider using smaller models:
   ```bash
   ollama pull nomic-embed-text      # Smaller embeddings
   ollama pull openchat              # Smaller LLM
   ```

### Issue: "ChromaDB already in use"

**Cause**: Another instance is running

**Solution**:
1. Close other RAG-Food instances
2. Rename/delete `chroma_db/` directory
3. Let it recreate on next run:
```bash
rm -rf ../chroma_db
python rag_run_local.py
```

### Issue: Slow query responses (15+ seconds)

**Cause**: Normal for local LLM, depends on hardware

**Common times by hardware:**
- **Decent laptop (i5/M1)**: 8-12 seconds
- **Older laptop**: 15-30 seconds
- **Desktop/Gaming PC**: 4-8 seconds
- **High-end GPU**: <2 seconds

**Solutions**:
1. Use higher-end hardware
2. Switch to cloud version for faster response
3. Close other applications to free resources

### Issue: Models not downloading

**Cause**: Network timeout or disk full

**Solution**:
```bash
# Set custom models directory
export OLLAMA_MODELS=/custom/path

# Try pulling again
ollama pull llama3.2

# Or manually download from https://ollama.ai/library
```

## Detailed Architecture

### Data Flow

```
User Input
    ↓
local-version/rag_run_local.py
    ↓
GET data/foods.json (110 items)
    ↓
For each food:
  1. Add region/type metadata
  2. Send to Ollama embedding endpoint
  3. Receive 1024-dim vector
  4. Store in ChromaDB
    ↓
User Query
    ↓
1. Embed question with Ollama
2. Search ChromaDB (cosine similarity)
3. Get top 3 documents
4. Build prompt with context
5. Send to Ollama LLM endpoint
6. Receive response
7. Print answer
```

### Ollama Endpoints Used

```python
# Embeddings
POST http://localhost:11434/api/embeddings
{
    "model": "mxbai-embed-large",
    "prompt": text
}

# LLM Response
POST http://localhost:11434/api/generate
{
    "model": "llama3.2",
    "prompt": prompt,
    "stream": false
}
```

## Performance Tuning

### Improve Embedding Speed
```bash
# Use faster embedding model (smaller)
ollama pull nomic-embed-text
# Edit rag_run_local.py, change EMBED_MODEL to nomic-embed-text
```

### Improve LLM Speed
```bash
# Use faster LLM (fewer parameters)
ollama pull openchat              # 7B model, faster
ollama pull neural-chat           # 7B specialized for chat
# Edit rag_run_local.py, change LLM_MODEL accordingly
```

### Batch Processing
For faster embedding of multiple items:
```python
# In rag_run_local.py, modify to batch embeddings
embeddings = [get_embedding(item['text']) for item in new_items]
```

## Advanced Configuration

### ChromaDB Settings

```python
# in rag_run_local.py
chroma_client = chromadb.PersistentClient(
    path="chroma_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

### Ollama Configuration

```bash
# Set Ollama host (if not localhost)
export OLLAMA_HOST=0.0.0.0:11434

# Set number of threads
export OLLAMA_NUM_THREAD=4

# Set context size
export OLLAMA_LLM_CONTEXT=2048
```

## Running Multiple Queries

```bash
# For batch processing (not interactive)
python << EOF
from rag_run_local import rag_query

queries = [
    "What are healthy mediterranean options?",
    "Which Indian dishes use chickpeas?",
    "Show me high-protein breakfast options?"
]

for query in queries:
    print(f"Q: {query}")
    answer = rag_query(query)
    print(f"A: {answer}\n")
EOF
```

## Docker Setup (Optional)

```dockerfile
FROM python:3.9-slim

# Install Ollama dependencies
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl https://ollama.ai/install.sh | sh

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Pull models
RUN ollama pull mxbai-embed-large
RUN ollama pull llama3.2

EXPOSE 11434
CMD ["sh", "-c", "ollama serve & python local-version/rag_run_local.py"]
```

```bash
docker build -t ragfood-local .
docker run -p 11434:11434 ragfood-local
```

## Next Steps

- Configure Ollama memory if needed
- Explore different embedding models
- Try alternative LLMs (neural-chat, openchat)
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system details
- Compare with [Cloud Version](setup-cloud.md) for performance

## Performance Expectations

| Metric | Value |
|--------|-------|
| Initial load | 30-60s (Ollama startup) |
| First query | 15-20s (cold model load) |
| Subsequent queries | 8-12s average |
| Memory usage | 3-4GB |
| CPU usage | 60-80% during inference |

---

**Status**: Development Ready ✅
**Best For**: Learning, offline use, privacy
**Version**: 2.0
**Last Updated**: April 8, 2026
