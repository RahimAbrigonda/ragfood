# RAG-Food Migration to Cloud Infrastructure - PRD

**ID**: PRD-001
**Status**: Draft
**Owner**: AI Assistant
**Created**: 2026-04-07
**Last Updated**: 2026-04-07

## Summary
Migrate the existing RAG-Food system from local ChromaDB + Ollama stack to cloud-based Upstash Vector + Groq infrastructure for improved scalability, reduced maintenance overhead, and enhanced performance.

## Problem Statement
- User need: Current system requires local Ollama server maintenance and ChromaDB storage management
- Business goal: Reduce operational complexity and improve system reliability for food recommendation RAG queries
- Success metric: 99% uptime, <2s query response time, zero local infrastructure management

## Target Users
- Primary: Developers maintaining RAG systems
- Secondary: End users querying food information

## Key Outcomes
1. Eliminate local vector database and LLM server management
2. Improve query performance through cloud infrastructure
3. Enable horizontal scaling for increased usage
4. Reduce operational costs and complexity

## Requirements

### Must Have
- [ ] Replace ChromaDB with Upstash Vector database
- [ ] Switch from Ollama embeddings to Upstash built-in embeddings
- [ ] Migrate LLM from local Ollama to Groq Cloud API
- [ ] Maintain existing food data integrity during migration
- [ ] Preserve query accuracy and response quality
- [ ] Update environment configuration for cloud services

### Should Have
- [ ] Implement data migration script for existing ChromaDB data
- [ ] Add error handling for cloud service failures
- [ ] Include monitoring and logging for cloud operations
- [ ] Update documentation with new architecture

### Could Have
- [ ] Add caching layer for frequently queried foods
- [ ] Implement rate limiting for API calls
- [ ] Add analytics for query patterns

## Technical Approach
- Stack: Python, Upstash Vector, Groq API, Requests library
- Architecture: Cloud-native RAG with managed vector storage and LLM inference
- Integration points: Upstash REST API, Groq REST API

## Architecture Changes

### Current Architecture
```
Local System:
User Query → Ollama Embeddings → ChromaDB Query → Context Retrieval → Ollama LLM → Response
```

### Proposed Architecture
```
Cloud System:
User Query → Upstash Embeddings → Upstash Vector Query → Context Retrieval → Groq LLM → Response
```

### Key Changes
1. **Vector Database**: ChromaDB (local SQLite) → Upstash Vector (managed cloud)
2. **Embeddings**: Ollama mxbai-embed-large (local) → Upstash built-in embeddings (cloud)
3. **LLM**: Ollama llama3.2 (local) → Groq API (cloud)

## Embedding Strategy

### Current: Ollama Embeddings
- Model: mxbai-embed-large
- Execution: Local via HTTP to Ollama server
- Dimensions: 1024
- Performance: Dependent on local hardware

### Proposed: Upstash Built-in Embeddings
- Model: Upstash managed embedding model
- Execution: Cloud API calls
- Dimensions: Compatible with Upstash Vector
- Performance: Optimized for Upstash infrastructure
- Benefits: No local model management, automatic updates

### Migration Plan
1. Test Upstash embedding compatibility with existing data
2. Re-embed all food documents using Upstash API
3. Update embedding generation code to use REST calls
4. Validate semantic similarity preservation

## LLM Changes

### Current: Local Ollama
- Model: llama3.2
- Execution: Local inference via HTTP
- Performance: Hardware-dependent
- Maintenance: Manual model updates

### Proposed: Groq Cloud
- Model: Groq-hosted LLM (compatible with llama3.2 performance)
- Execution: Cloud API calls
- Performance: Optimized for speed and reliability
- Maintenance: Managed service

### Migration Plan
1. Test Groq API compatibility with existing prompts
2. Update LLM call from local HTTP to Groq REST API
3. Implement API key authentication
4. Validate response quality and latency

## Risks & Assumptions
- Risk: Upstash embeddings may have different semantic properties | Mitigation: A/B testing with sample queries
- Risk: Groq API downtime | Mitigation: Implement retry logic and fallback options
- Assumption: Upstash and Groq APIs are stable and well-documented | Validation: Review API documentation and test endpoints
- Risk: Data migration may lose precision | Mitigation: Preserve original embeddings for rollback

## Success Criteria
- Query accuracy: >95% maintained from current system
- Response time: <2 seconds average
- Uptime: 99.5% over 30 days
- Zero local infrastructure dependencies

## Implementation Plan
1. Phase 1: Setup and testing (1 week) - Configure Upstash and Groq credentials, test APIs
2. Phase 2: Data migration (1 week) - Migrate food data to Upstash Vector with new embeddings
3. Phase 3: Code updates (1 week) - Update rag_run.py for cloud services
4. Phase 4: Testing and validation (1 week) - End-to-end testing, performance validation

## Resources
- Upstash Vector Documentation: https://docs.upstash.com/vector
- Groq API Documentation: https://console.groq.com/docs
- Current Codebase: rag_run.py
- Data Source: foods.json
