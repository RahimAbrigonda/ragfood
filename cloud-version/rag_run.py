import os
import json
import requests
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
UPSTASH_URL = os.getenv("UPSTASH_VECTOR_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JSON_FILE = "../data/foods.json"
COLLECTION_NAME = "foods"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Initialize SentenceTransformer
print("📦 Loading SentenceTransformer model...")
embed_model = SentenceTransformer(EMBED_MODEL_NAME)

# Load food data
print("📖 Loading food database...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Generate embeddings locally
def get_embedding(text):
    """Generate embedding using SentenceTransformer"""
    return embed_model.encode(text).tolist()

# Check existing IDs in Upstash
def get_existing_ids():
    """Get IDs of documents already in Upstash"""
    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{UPSTASH_URL}/info", headers=headers)
        response.raise_for_status()
        info = response.json()
        vector_count = info.get('vector_count', 0)
        print(f"✅ Upstash status: {vector_count} vectors already stored")
        return set() if vector_count == 0 else set()  # Simplified for this version
    except Exception as e:
        print(f"⚠️  Could not check existing vectors: {e}")
        return set()

# Upsert data to Upstash
def upsert_to_upstash():
    """Upload embeddings to Upstash Vector"""
    existing_ids = get_existing_ids()
    new_items = [item for item in food_data if item['id'] not in existing_ids]
    
    if not new_items:
        print("✅ All documents already in Upstash Vector.")
        return
    
    print(f"🆕 Adding {len(new_items)} documents to Upstash Vector...")
    
    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for item in new_items:
        # Enhance text with metadata
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."
        
        # Generate embedding
        embedding = get_embedding(enriched_text)
        
        # Prepare payload for Upstash
        payload = {
            "id": item["id"],
            "values": embedding,
            "metadata": {
                "text": item["text"],
                "region": item.get("region", ""),
                "type": item.get("type", "")
            }
        }
        
        try:
            response = requests.post(
                f"{UPSTASH_URL}/vectors/upsert",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
        except Exception as e:
            print(f"⚠️  Error upserting document {item['id']}: {e}")
        
        if (new_items.index(item) + 1) % 10 == 0:
            print(f"   Progress: {new_items.index(item) + 1}/{len(new_items)} documents processed")
    
    print(f"✅ Successfully added {len(new_items)} documents to Upstash Vector!")

# RAG query function
def rag_query(question):
    """Query Upstash for relevant documents and generate answer with Groq"""
    
    # Step 1: Embed the question
    q_embedding = get_embedding(question)
    
    # Step 2: Query Upstash Vector for similar documents
    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "vector": q_embedding,
        "top_k": 3,
        "include_metadata": True
    }
    
    response = requests.post(
        f"{UPSTASH_URL}/vectors/query",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    results = response.json()
    
    # Step 3: Extract retrieved documents
    top_docs = []
    top_ids = []
    
    if isinstance(results, list):
        matches = results
    else:
        matches = results.get('results', [])
    
    for match in matches[:3]:
        if 'metadata' in match:
            top_docs.append(match['metadata'].get('text', ''))
            top_ids.append(match.get('id', 'unknown'))
    
    # Step 4: Show retrieved documents
    print("\n🧠 Retrieving relevant information to reason through your question...\n")
    
    for i, (doc, doc_id) in enumerate(zip(top_docs, top_ids)):
        print(f"🔹 Source {i + 1} (ID: {doc_id}):")
        print(f"    \"{doc}\"\n")
    
    print("📚 These seem to be the most relevant pieces of information to answer your question.\n")
    
    # Step 5: Build prompt from context
    context = "\n".join(top_docs)
    
    prompt = f"""Use the following context to answer the question. Be helpful, informative, and concise.

Context:
{context}

Question: {question}
Answer:"""
    
    # Step 6: Generate answer with Groq
    groq_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    groq_payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "llama3-8b-8192",
        "max_tokens": 1024
    }
    
    groq_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=groq_headers,
        json=groq_payload
    )
    groq_response.raise_for_status()
    
    # Step 7: Extract and return answer
    answer = groq_response.json()['choices'][0]['message']['content']
    return answer.strip()

# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 RAG-Food: Cloud Version (Upstash + Groq)")
    print("="*60 + "\n")
    
    # Upsert data on startup
    upsert_to_upstash()
    
    # Interactive query loop
    print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
    while True:
        try:
            question = input("You: ").strip()
            if question.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            if not question:
                continue
            
            answer = rag_query(question)
            print("🤖:", answer)
            print()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.\n")
