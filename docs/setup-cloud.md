# 🚀 Cloud Version Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Internet connection
- Upstash Vector account (free tier available)
- Groq API account (free tier available)

## Step 1: Create Accounts & Get API Keys

### Upstash Vector Setup

1. Go to https://console.upstash.com/
2. Sign up or log in
3. Click "Create Database" → Select "Vector"
4. Configure:
   - **Name**: ragfood
   - **Region**: us-east-1 (closest to you)
   - **Type**: Vector
5. Click "Create"
6. On the dashboard, copy:
   - **REST URL**: `https://your-db-us1-vector.upstash.io`
   - **REST Token**: Your authentication token

### Groq API Setup

1. Go to https://console.groq.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy your API key (starts with `gsk_`)

> **Keep these credentials secure!** Do not share or commit to Git.

## Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/gocallum/ragfood.git
cd ragfood

# Checkout cloud-migration branch
git checkout cloud-migration
```

## Step 3: Create Virtual Environment

```bash
# On Windows
python -m venv ENV
.\ENV\Scripts\activate

# On macOS/Linux
python3 -m venv ENV
source ENV/bin/activate
```

## Step 4: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "requests|sentence-transformers|python-dotenv"
```

**Expected output should show:**
- requests (2.31.0 or newer)
- sentence-transformers (2.2.2 or newer)
- python-dotenv (1.0.0 or newer)

## Step 5: Configure Environment Variables

### Option A: Using `.env` File (Recommended)

```bash
# Create .env file in project root
cat > .env << EOF
UPSTASH_VECTOR_REST_URL="https://your-instance-us1-vector.upstash.io"
UPSTASH_VECTOR_REST_TOKEN="your_upstash_token"
GROQ_API_KEY="gsk_your_groq_key"
EOF
```

Replace with your actual credentials from Step 1.

### Option B: Using Environment Variables

```bash
# Windows PowerShell
$env:UPSTASH_VECTOR_REST_URL = "https://your-instance-us1-vector.upstash.io"
$env:UPSTASH_VECTOR_REST_TOKEN = "your_token"
$env:GROQ_API_KEY = "gsk_your_key"

# macOS/Linux
export UPSTASH_VECTOR_REST_URL="https://your-instance-us1-vector.upstash.io"
export UPSTASH_VECTOR_REST_TOKEN="your_token"
export GROQ_API_KEY="gsk_your_key"
```

### Verify Configuration

```bash
# Test that your .env is loaded correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ .env loaded' if os.getenv('GROQ_API_KEY') else '❌ config missing')"
```

## Step 6: Run Cloud Version

```bash
# Navigate to cloud version directory
cd cloud-version

# Run the application
python rag_run.py
```

### Expected Output

```
============================================================
🚀 RAG-Food: Cloud Version (Upstash + Groq)
============================================================

📦 Loading SentenceTransformer model...
📖 Loading food database...
✅ Upstash status: 0 vectors already stored
🆕 Adding 110 documents to Upstash Vector...
   Progress: 10/110 documents processed
   Progress: 20/110 documents processed
   ...
✅ Successfully added 110 documents to Upstash Vector!

🧠 RAG is ready. Ask a question (type 'exit' to quit):

You: 
```

## Step 7: Test with Queries

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

### Issue: "401 Unauthorized" from Groq

**Cause**: Invalid API key

**Solution**:
1. Verify API key in `.env` file exactly matches console.groq.com
2. Ensure no extra spaces or quotes
3. Check API key hasn't been revoked
4. Generate new key if needed

### Issue: "Connection refused" to Upstash

**Cause**: Network or credential issue

**Solution**:
1. Verify internet connection
2. Check UPSTASH_VECTOR_REST_URL is correct
3. Verify UPSTASH_VECTOR_REST_TOKEN is exact
4. Test URL directly: `curl -H "Authorization: Bearer {token}" https://your-url/info`

### Issue: "ImportError: No module named 'sentence_transformers'"

**Cause**: Missing dependencies

**Solution**:
```bash
pip install sentence-transformers
pip install -r requirements.txt
```

### Issue: Model download timeout

**Cause**: Slow internet or disk space

**Solution**:
```bash
# Wait longer or check disk space
df -h  # Check free space

# Set Hugging Face cache
export HF_HOME=/path/to/cache
python rag_run.py
```

### Issue: Slow first run

**Cause**: Downloading SentenceTransformer model (~400MB)

**Solution**: This is normal. First run takes 2-3 minutes. Subsequent runs are fast.

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions
- Review [COMPARISON_ANALYSIS.md](COMPARISON_ANALYSIS.md) for performance data
- Explore [README.md](../README.md) for full documentation

## Running with Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY data/ data/
COPY cloud-version/ cloud-version/
COPY .env .env

CMD ["python", "cloud-version/rag_run.py"]
```

```bash
# Build and run
docker build -t ragfood .
docker run -e UPSTASH_VECTOR_REST_URL=$UPSTASH_VECTOR_REST_URL \
           -e UPSTASH_VECTOR_REST_TOKEN=$UPSTASH_VECTOR_REST_TOKEN \
           -e GROQ_API_KEY=$GROQ_API_KEY \
           ragfood
```

## Cost Estimation

### Monthly Costs (Estimate)

For 100 queries/day (3000/month):

| Service | Cost | Notes |
|---------|------|-------|
| Upstash Vector | $0.60 | 3000 queries @ $0.0002 each |
| Groq API | $0.015 | ~30 input + output tokens avg |
| Total | ~$0.62 | Very affordable! |

### Free Tier Limits

- **Groq**: 30 requests/minute, unlimited queries/month
- **Upstash**: 14 days data retention, 1GB storage

---

**Status**: Ready for production use ✅
**Version**: 2.0
**Last Updated**: April 8, 2026
