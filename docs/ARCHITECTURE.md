# 🏗️ Architecture Documentation

## Overview

RAG-Food implements a **Retrieval-Augmented Generation** system with dual architecture support:

1. **Local Architecture** (Week 2): ChromaDB + Ollama (local services)
2. **Cloud Architecture** (Week 3+): Upstash Vector + Groq (cloud services)

---

## Local Architecture

### System Flow

```
User Query
    ↓
Local Ollama (Port 11434)
    ├─ Embedding Model: mxbai-embed-large
    └─ LLM Model: llama3.2
    ↓
ChromaDB
    ├─ Storage: SQLite (chroma_db/)
    ├─ Vectors: 1024-dimensional
    └─ Retrieval: Top 3 similar documents
    ↓
Context + Question → Ollama LLM
    ↓
Natural Language Response
```

### Components

#### 1. **Ollama Server**
- **Purpose**: Local LLM and embedding service
- **Port**: 11434
- **Requirements**:
  - mxbai-embed-large (1024 dims)
  - llama3.2 (LLM)
- **Memory**: ~4GB
- **Startup Time**: 30-60 seconds

#### 2. **ChromaDB**
- **Purpose**: Vector database for document storage
- **Backend**: SQLite
- **Location**: `chroma_db/` directory
- **Collection**: "foods"
- **Retrieval**: Cosine similarity search

#### 3. **Application Layer** (local-version/rag_run_local.py)
- Loads JSON data
- Generates embeddings via Ollama
- Stores in ChromaDB
- Retrieves similar documents
- Sends context to Ollama LLM

### Advantages

- ✅ **No internet required** - fully offline
- ✅ **Privacy**: All data stays local
- ✅ **Free**: No API costs
- ✅ **Customizable**: Full control over models
- ✅ **Learning**: Understand each component

### Disadvantages

- ❌ **Hardware dependent**: Needs powerful CPU/GPU
- ❌ **High memory**: 4GB+ RAM required
- ❌ **Slow**: 8-12 seconds per query
- ❌ **Manual maintenance**: Version updates required
- ❌ **Single user**: Limited concurrency
- ❌ **Setup complexity**: Multiple local dependencies

---

## Cloud Architecture

### System Flow

```
User Query
    ↓
Sentence-Transformers (Local)
    ├─ Model: all-MiniLM-L6-v2 (384-dim)
    └─ Process: Local embedding generation
    ↓
Upstash Vector (Cloud) - REST API
    ├─ Endpoint: /vectors/query
    ├─ Storage: Managed cloud
    └─ Retrieval: Top 3 similar documents
    ↓
Context + Question → Groq API
    ├─ Model: llama3-8b-8192
    ├─ Endpoint: chat/completions
    └─ Response: Streaming or complete
    ↓
Natural Language Response
```

### Components

#### 1. **Sentence-Transformers** (Local)
- **Purpose**: Lightweight embedding model
- **Model**: all-MiniLM-L6-v2
- **Dimensions**: 384 (vs 1024 for Ollama)
- **Speed**: <100ms per embedding
- **Memory**: ~400MB
- **Advantage**: Works offline, no server needed

#### 2. **Upstash Vector Database** (Cloud)
- **URL**: `https://{project}-us1-vector.upstash.io`
- **Auth**: Bearer token
- **API Endpoints**:
  - `/info` - Check vector count
  - `/vectors/upsert` - Add/update vectors
  - `/vectors/query` - Semantic search
  - `/delete` - Remove vectors
- **Pricing**: Pay-per-use ($0.0002 per 1K query vectors)
- **Storage**: Managed, replicated

#### 3. **Groq API** (Cloud)
- **Purpose**: Fast LLM inference
- **Model**: llama3-8b-8192 (8K context)
- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Auth**: Bearer token (API key)
- **Speed**: <100ms response time
- **Pricing**: $0.005 per 1M input tokens
- **Rate Limit**: 30 requests/minute (free tier)

#### 4. **Application Layer** (cloud-version/rag_run.py)
- Loads JSON data
- Generates embeddings with Sentence-Transformers
- Upserts to Upstash Vector
- Queries Upstash for similar documents
- Sends context to Groq API
- Returns final answer

### Advantages

- ✅ **Fast**: 2-3 seconds per query
- ✅ **Scalable**: Handles thousands of users
- ✅ **Low resources**: <200MB local memory
- ✅ **Reliable**: 99.9% uptime SLA
- ✅ **Easy setup**: Just API keys
- ✅ **Managed**: No maintenance needed
- ✅ **Pay-as-you-go**: Only pay for usage

### Disadvantages

- ❌ **Internet required**: Cloud-dependent
- ❌ **Costs**: ~$10-20/month for production
- ❌ **API limits**: Rate limiting on free tier
- ❌ **Data privacy**: Data goes through cloud
- ❌ **Vendor lock-in**: Dependent on services

---

## Comparison Matrix

| Aspect | Local | Cloud |
|--------|-------|-------|
| **Embedding** | Ollama (1024-dim) | SentenceTransformer (384-dim) |
| **Vector DB** | ChromaDB (local) | Upstash (managed) |
| **LLM** | Ollama (local) | Groq (cloud) |
| **Query Speed** | 8-12s | 2-3s |
| **Memory** | 4GB+ | <200MB |
| **Setup** | 30 min | 5 min |
| **Uptime** | On-demand | 99.9% |
| **Cost** | $0 | $5-20/month |
| **Privacy** | ✅ 100% | ⚠️ Shared |

---

## Technical Decisions

### Why Sentence-Transformers?

- **Lightweight**: 384-dim vs 1024-dim Ollama
- **Fast**: <100ms per embedding
- **Quality**: Proven on semantic search tasks
- **No server**: Run locally on client
- **Compatible**: Works with Upstash Vector

### Why Upstash Vector?

- **Managed**: No infrastructure to maintain
- **Fast**: SSD-backed, optimized for vectors
- **Reliable**: Multi-replica, automatic failover
- **Cost-effective**: Pay only for what you use
- **API-first**: REST endpoints, easy integration

### Why Groq?

- **Speed**: Specialized LLM inference hardware
- **Cost**: Competitive pricing, free tier with limits
- **Reliability**: 99.9% uptime guarantee
- **API**: OpenAI-compatible chat endpoint
- **Model**: llama3-8b sufficient for Q&A tasks

---

## Data Flow Details

### Local Version

```python
# 1. Load data
foods.json → Python dict (110 items)

# 2. Generate embeddings
text → Ollama mxbai-embed-large → 1024-dim vector

# 3. Store
vector + id + metadata → ChromaDB collection

# 4. Query
question → embedding → cosine similarity → top 3 docs

# 5. Generate answer
context + question + prompt → Ollama llama3.2 → response
```

### Cloud Version

```python
# 1. Load data
foods.json → Python dict (110 items)

# 2. Generate embeddings (local)
text → SentenceTransformer → 384-dim vector

# 3. Store
vector + id + metadata → HTTP POST /vectors/upsert → Upstash

# 4. Query
question → embedding → HTTP POST /vectors/query → Upstash

# 5. Generate answer
context + question + prompt → HTTP POST /chat/completions → Groq
```

---

## Scaling Considerations

### Local (Limited)

- **Single machine**: ~110 documents max efficiently
- **Concurrent users**: 1 (sequential processing)
- **Storage**: Limited by disk
- **Scaling**: Requires more hardware

### Cloud (Unlimited)

- **Document count**: 100K+ easily scalable
- **Concurrent users**: Thousands supported
- **Storage**: Unlimited (pay per GB-month)
- **Scaling**: Automatic, transparent

---

## Security Considerations

### Local
- ✅ No external data leakage
- ✅ No API keys exposed
- ❌ Vulnerable to local compromise

### Cloud
- ⚠️ API keys must be protected
- ✅ Upstash uses TLS encryption
- ✅ API requests authenticated
- ✅ No data stored locally on instance

**Best Practice**: Use `.env` file, never commit credentials to Git

---

## Performance Characteristics

### Latency Breakdown (Cloud)

```
Network latency (client → Groq):        500ms
Embedding generation local:              50ms
Upstash query:                          400ms
Groq inference:                        1000ms (1 sec)
Network latency (Groq → client):        500ms
────────────────────────────────────────────
Total:                                ~2.4 seconds
```

### Local Latency Breakdown

```
Ollama embedding:                      2000ms
ChromaDB search:                        100ms
Ollama LLM:                            6000ms
────────────────────────────────────────────
Total:                                ~8.1 seconds
```

---

## Recommended Architecture Selection

### Use **Local Version** if:
- Strict data privacy requirements
- Offline capability needed
- No budget for cloud services
- Educational/learning purposes
- Low query volume (<10/day)

### Use **Cloud Version** if:
- Performance is critical
- High availability needed
- Scaling to multiple users
- Cost optimization important
- Limited server resources available
- Production deployment

---

## Future Architecture Enhancements

### Hybrid Approach
- Embed locally, sync to Upstash
- Cache recent queries locally
- Fallback: Ollama if internet down

### Vector Search Optimization
- Chunking: Break documents into smaller pieces
- Reranking: Use second-stage ranker for accuracy
- Namespaces: Organize vectors by category

### Multi-model
- Multiple embedding models (trade speed vs accuracy)
- Multiple LLMs (switching based on query complexity)
- Ensemble approaches

