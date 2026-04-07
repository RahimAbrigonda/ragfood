# 🔍 Troubleshooting Guide

## Quick Reference

### Cloud Version Issues

| Error | Cause | Solution |  
|-------|-------|----------|
| `401 Unauthorized` | Invalid API key | Check `.env` credentials |
| `Connection refused` | Network/Upstash down | Verify internet, check URL |
| `ModuleNotFoundError` | Missing dependencies | `pip install -r requirements.txt` |
| Empty results | No vectors in Upstash | Run upsert first |
| Slow responses | API rate limit | Wait or upgrade plan |

### Local Version Issues

| Error | Cause | Solution |  
|-------|-------|----------|
| `Connection refused` | Ollama not running | Run `ollama serve` in new terminal |
| `Model not found` | Ollama models missing | `ollama pull llama3.2 mxbai-embed-large` |
| Out of memory | System RAM exhausted | Close apps, reduce batch size |
| Permission denied | chmod issue | `chmod -R 755 chroma_db/` |
| Takes 20+ seconds | Hardware too slow | Normal for older machines |

---

## Detailed Solutions

### Networking Issues

#### "Connection refused" on API calls

**Error message:**
```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='api.groq.com', port=443):
Max retries exceeded with url
```

**Causes:**
- API server down
- Network connectivity issue
- Firewall blocking
- VPN/proxy interference

**Solutions:**

1. **Test internet connection:**
```bash
ping google.com
ping api.groq.com  # Test Groq connectivity
ping upstash.com   # Test Upstash connectivity
```

2. **Test API endpoints directly:**
```bash
# Test Groq
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.groq.com/openai/v1/models

# Test Upstash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-db-us1-vector.upstash.io/info
```

3. **Check firewall:**
```bash
# Windows: Check Windows Defender Firewall settings
# macOS: System Preferences → Security & Privacy → Firewall
# Linux: sudo ufw status
```

4. **Try different network:**```bash
# Try mobile hotspot or different WiFi
# Check if ISP blocks certain endpoints
```

---

### Authentication Issues

#### "401 Unauthorized" from Groq/Upstash

**Error message:**
```
HTTPError: 401 Unauthorized
Response: {"error": "Unauthorized"}
```

**Causes:**
- Wrong API key format
- Expired API key
- API key revoked
- Typos in `.env` file

**Solutions:**

1. **Verify `.env` format:**
```bash
# Check .env file isn't corrupted
cat .env
# Should look exactly like:
# GROQ_API_KEY=gsk_abc123...
# (no quotes, no extra spaces)
```

2. **Generate new API keys:**
   - Groq: https://console.groq.com/keys
   - Upstash: https://console.upstash.com/

3. **Test credentials directly:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROQ_API_KEY")
print(f"Key loaded: {key[:10]}...")  # Should start with gsk_
```

4. **Check for encoding issues:**
```bash
# Windows PowerShell - check for BOM
file .env  # Should be "ASCII text"
```

---

### Dependency Issues

#### "ModuleNotFoundError: No module named '...'"

**Error message:**
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solutions:**

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Verify installation:**
```bash
pip list | findstr sentence-transformers  # Windows
pip list | grep sentence-transformers     # macOS/Linux
```

3. **Force reinstall:**
```bash
pip install --force-reinstall sentence-transformers
```

4. **Check Python version:**
```bash
python --version  # Should be 3.8+
```

5. **Try alternative installation:**
```bash
pip install sentence-transformers --no-cache-dir
```

---

### Ollama Issues (Local Version)

#### Ollama service won't start

**Symptoms:**
- "Connection refused on localhost:11434"
- `requests.exceptions.ConnectionError`

**Solutions:**

1. **Start Ollama service:**
```bash
ollama serve
# Or use system service:
systemctl start ollama  # Linux
launchctl start com.ollama.app  # macOS
```

2. **Check if already running:**
```bash
# Windows
netstat -ano | findstr :11434

# macOS/Linux
lsof -i :11434
```

3. **Kill conflicting process:**
```bash
# Windows
taskkill /PID {PID} /F

# macOS/Linux
kill {PID}
```

4. **Reinstall Ollama:**
   - Uninstall from system
   - Delete settings: `~/.ollama`
   - Reinstall from https://ollama.ai

#### Models not found

**Error:**
```
Error: "llama3.2" not found, pull the model first
```

**Solutions:**

1. **Pull missing models:**
```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

2. **Check installed models:**
```bash
ollama list
```

3. **Use alternative models:**
```bash
# Faster embedding (smaller)
ollama pull nomic-embed-text

# Faster LLM (smaller)
ollama pull neural-chat

# Edit rag_run_local.py and change model names
```

#### High memory usage / Out of memory

**Symptoms:**
- System becomes very slow
- Ollama crashes
- Computer freezes

**Solutions:**

1. **Check available memory:**
```bash
# Windows: Task Manager → Performance
# macOS: Activity Monitor
# Linux: free -h
```

2. **Use lighter models:**
```bash
ollama pull nomic-embed-text      # 274MB vs 273MB
ollama pull openchat              # 3.8GB vs llama3.2
```

3. **Limit Ollama threads:**
```bash
export OLLAMA_NUM_THREAD=2  # Use 2 threads instead of all
```

4. **Reduce context size:**
```bash
export OLLAMA_LLM_CONTEXT=1024  # Smaller context window
```

5. **Run on different machine:**
   - Use cloud version instead
   - Or use higher-spec hardware

---

### Data & Database Issues

#### ChromaDB permission errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'chroma_db'
```

**Solutions:**

1. **Fix folder permissions:**
```bash
# Windows: No special fix needed typically
# macOS/Linux
chmod -R 755 chroma_db/
```

2. **Delete and recreate database:**
```bash
rm -rf chroma_db
python local-version/rag_run_local.py  # Will recreate
```

3. **Run as different user:**
```bash
sudo python local-version/rag_run_local.py
```

#### Corrupted ChromaDB

**Symptoms:**
- Various cryptic database errors
- Searches return no results
- Database locked errors

**Solutions:**

1. **Reset database:**
```bash
# Backup first
mv chroma_db chroma_db.backup

# Run again to recreate
python local-version/rag_run_local.py
```

2. **Check database integrity:**
```bash
sqlite3 chroma_db/chroma.sqlite3
sqlite> pragma integrity_check;
sqlite> .quit
```

---

### Vector Search Issues

#### Empty results from queries

**Symptoms:**
- Queries return no documents
- "No results found"

**Causes:**
- Vectors not upserted yet
- Wrong embedding dimensions
- Query doesn't match documents semantically

**Solutions:**

1. **Verify vectors exist:**
```bash
# Cloud version
curl -H "Authorization: Bearer {TOKEN}" \
  https://your-db-us1-vector.upstash.io/info

# Should show: {"vector_count": 110}
```

2. **Check embedding dimensions:**
```python
# Verify dimensions in cloud-version/rag_run.py
EMBEDDING_DIM = 384  # Must match SentenceTransformer output
```

3. **Manually upsert test vector:**
```python
import requests
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "id": "test",
    "values": [0.1] * 384,  # 384 dimensions
    "metadata": {"test": "true"}
}
response = requests.post(
    f"{url}/vectors/upsert",
    headers=headers,
    json=payload
)
print(response.status_code, response.text)
```

---

### Performance Issues

#### Very slow responses (20+ seconds cloud)

**Causes:**
- API rate limiting
- Network latency
- Queue buildup
- Groq API congestion

**Solutions:**

1. **Wait between requests:**
```python
import time
time.sleep(2)  # 2 second delay
```

2. **Check API rate limits:**
```bash
# Groq free tier: 30 requests/minute
# Upstash free tier: Generous limits
```

3. **Upgrade API plan:**
   - Groq: https://console.groq.com/billing/subscriptions
   - Upstash: https://console.upstash.com/account/plan

4. **Use caching:**
```python
# Cache common questions
cache = {}
if question in cache:
    return cache[question]
```

#### Very slow responses (30+ seconds local)

**Normal for local setup on most hardware.**

**Optimization:**
```bash
# Use faster model
ollama pull neural-chat  # ~7B vs llama3.2 ~8B

# Use GPU if available
export CUDA_VISIBLE_DEVICES=0
ollama serve
```

---

### Files & Paths Issues

#### "File not found" errors

**Causes:**
- Running from wrong directory
- Relative paths broken
- File structure not created

**Solutions:**

1. **Check working directory:**
```bash
# Should be in ragfood/
pwd
ls -la  # Should see local-version/, cloud-version/, data/, etc.
```

2. **Verify file structure:**
```bash
# Check data file exists
ls data/foods.json

# Check local version exists
ls local-version/rag_run_local.py
ls cloud-version/rag_run.py
```

3. **Fix paths in code:**
```python
# If running cloud-version/rag_run.py:
JSON_FILE = "../data/foods.json"  # Correct

# If running from root:
JSON_FILE = "data/foods.json"     # Also correct
```

---

### Version-Specific Issues

#### Cloud version specific

**"Vector dimension mismatch"**
- SentenceTransformers outputs 384-dim
- Verify `EMBEDDING_DIM = 384` in code

**"Invalid metadata"**
- Metadata must be JSON-serializable
- Don't store complex objects directly

#### Local version specific

**"Ollama: model is not loaded"**
- Edit model name in code
- Or pull the model first

**"ChromaDB collection empty"**
- First run should populate automatically
- If not, manually trigger upsert

---

## Getting Help

### Before asking for help

1. Check logs:
   - Full error message (not just first line)
   - Stack trace showing line numbers
   - Environment details (OS, Python version)

2. Try solutions above in order

3. Check documentation:
   - [ARCHITECTURE.md](ARCHITECTURE.md)
   - [setup-cloud.md](setup-cloud.md)
   - [setup-local.md](setup-local.md)

### Getting support

1. **GitHub Issues**: https://github.com/gocallum/ragfood/issues
   - Include error message, OS, Python version
   - Include which version (local/cloud)
   - Include steps to reproduce

2. **Check existing issues**:
   - Search by error message
   - Check closed issues too

3. **Debugging info to share**:
```bash
# System info
python --version
pip list

# Logs
python -u cloud-version/rag_run.py 2>&1 | tee output.log

# Credentials verification (don't share keys!)
echo "Keys exist: $(test -f .env && echo 'YES' || echo 'NO')"
```

---

## Advanced Debugging

### Enable verbose logging

```python
# Add to rag_run.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for requests library
import logging
logging.getLogger('requests').setLevel(logging.DEBUG)
```

### Test API endpoints separately

```python
import requests

# Test Upstash
url = "https://your-db-us1-vector.upstash.io/info"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(url, headers=headers)
print(response.status_code)
print(response.json())

# Test Groq
url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {key}"}
response = requests.get(url, headers=headers)
print(response.json())
```

### Monitor API calls

```bash
# Windows: Use Fiddler or Charles
# macOS: Use Charles Proxy
# Linux: Use tcpdump

tcpdump -i any -n port 443 | grep -E "groq|upstash"
```

---

**Last Updated**: April 8, 2026  
**Version**: 2.0
