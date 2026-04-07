import os
import json
import requests
from typing import List, Dict, Any

# Constants
UPSTASH_URL = "https://smiling-monarch-63542-us1-vector.upstash.io"
UPSTASH_TOKEN = "ABkFMHNtaWxpbmctbW9uYXJjaC02MzU0Mi11czFhZG1pbk56UmxZMlF3TlRFdE5EQTFaUzAwT1RNM0xUa3laRGt0TURJMk5qbGpPREpsTkdZMA=="
GROQ_API_KEY = "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"
COLLECTION_NAME = "foods"
JSON_FILE = "foods.json"

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Headers for Upstash
upstash_headers = {
    "Authorization": f"Bearer {UPSTASH_TOKEN}",
    "Content-Type": "application/json"
}

# Upstash embedding function (using sentence-transformers locally for now)
def get_embedding(text: str) -> List[float]:
    # For now, using a simple approach - in production you'd want a cloud embedding service
    # Let's use a local sentence transformer
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        return model.encode(text).tolist()
    except ImportError:
        # Fallback: simple hash-based embedding (not good for production)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        # Create a 384-dimensional vector from hash (same as MiniLM)
        hash_bytes = hash_obj.digest()
        return [float(b) / 255.0 for b in hash_bytes] * 16  # 16 * 24 = 384

# Check existing vectors in Upstash
def get_existing_ids() -> set:
    try:
        # Try to query with a zero vector to get some results
        response = requests.post(
            f"{UPSTASH_URL}/vectors/query",
            headers=upstash_headers,
            json={"vector": [0.0] * 384, "topK": 1000, "includeMetadata": True}
        )
        if response.status_code == 200:
            results = response.json()
            return {item["id"] for item in results.get("results", [])}
        return set()
    except:
        return set()

# Add new items to Upstash Vector
existing_ids = get_existing_ids()
new_items = [item for item in food_data if item['id'] not in existing_ids]

if new_items:
    print(f"🆕 Adding {len(new_items)} new documents to Upstash Vector...")
    for item in new_items:
        # Enhance text with region/type for better context
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."

        # Get embedding
        embedding = get_embedding(enriched_text)

        # Upsert single vector
        vector_data = {
            "vectors": [{
                "id": item["id"],
                "vector": embedding,
                "metadata": {
                    "text": item["text"],
                    "region": item.get("region", ""),
                    "type": item.get("type", ""),
                    "enriched_text": enriched_text
                }
            }]
        }

        response = requests.post(
            f"{UPSTASH_URL}/vectors/upsert",
            headers=upstash_headers,
            json=vector_data
        )
        if response.status_code not in [200, 201]:
            print(f"Failed to upsert {item['id']}: {response.text}")
        else:
            print(f"✓ Added {item['id']}")

    print("✅ Successfully added new documents to Upstash Vector.")
else:
    print("✅ All documents already in Upstash Vector.")

# RAG query function
def rag_query(question: str) -> str:
    # Step 1: Embed the user question
    q_emb = get_embedding(question)

    # Step 2: Query Upstash Vector
    query_data = {
        "vector": q_emb,
        "topK": 3,
        "includeMetadata": True
    }

    response = requests.post(
        f"{UPSTASH_URL}/vectors/query",
        headers=upstash_headers,
        json=query_data
    )
    response.raise_for_status()
    results = response.json()

    # Step 3: Extract documents
    top_docs = []
    top_ids = []
    for result in results.get("results", []):
        metadata = result.get("metadata", {})
        top_docs.append(metadata.get("text", ""))
        top_ids.append(result["id"])

    # Step 4: Show friendly explanation of retrieved documents
    print("\n🧠 Retrieving relevant information to reason through your question...\n")

    for i, doc in enumerate(top_docs):
        print(f"🔹 Source {i + 1} (ID: {top_ids[i]}):")
        print(f"    \"{doc[:200]}...\"\n")  # Truncate for display

    print("📚 These seem to be the most relevant pieces of information to answer your question.\n")

    # Step 5: Build prompt from context
    context = "\n".join(top_docs)

    prompt = f"""Use the following context to answer the question about healthy Mediterranean food options.

Context:
{context}

Question: {question}

Provide a helpful, accurate answer focusing on healthy Mediterranean dietary options. Include nutritional benefits, ingredients, and cultural context where relevant."""

    # Step 6: Generate answer with Groq
    groq_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )
    groq_response.raise_for_status()

    # Step 7: Return final result
    return groq_response.json()["choices"][0]["message"]["content"].strip()


# Interactive loop
print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
while True:
    question = input("You: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break
    answer = rag_query(question)
    print("🤖:", answer)
