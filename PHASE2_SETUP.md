# Phase 2 Setup - Pinecone Integration

## What's Changing:

**Episodic Memory:** NeonDB → **Pinecone** (dedicated vector DB)
**Semantic Memory:** Still in NeonDB (for now)

## Setup Steps:

### 1. Get Pinecone API Key

1. Go to https://www.pinecone.io
2. Click "Sign Up" (free)
3. Once logged in, go to "API Keys"
4. Click "Create API Key"
5. Copy the key (starts with `pcsk_...` or similar)

### 2. Add API Key to Secrets

Open `.streamlit/secrets.toml` and replace:
```toml
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY_HERE"
```

With your actual key:
```toml
PINECONE_API_KEY = "pcsk_your_actual_key_here"
```

### 3. Install New Dependencies

```bash
pip install langchain-pinecone pinecone-client
```

Or install everything:
```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

## What Happens on First Run:

1. Pinecone creates an index called `episodic-memory`
2. Index specs:
   - Dimension: 384 (matches embedding model)
   - Metric: cosine similarity
   - Region: us-east-1 (AWS)
   - Type: Serverless (free tier)

3. All new episodic memories go to Pinecone
4. Semantic memories still go to NeonDB

## Architecture Now:

```
User Input
    ↓
Groq LLM
    ↓
┌─────────────────┐    ┌──────────────┐
│   Pinecone      │    │   NeonDB     │
│   (Episodic)    │    │  (Semantic)  │
│                 │    │              │
│ Conversations   │    │   Facts      │
│ Context         │    │   Truths     │
└─────────────────┘    └──────────────┘
```

## Benefits:

✅ **Better Performance** - Pinecone is optimized for vector search
✅ **Scalability** - Can handle millions of vectors
✅ **Reliability** - Managed service, no database sleeping
✅ **Metadata Filtering** - Advanced query capabilities
✅ **Free Tier** - 1 index, 100K vectors, plenty for chatbot

## Testing:

1. Start fresh conversation
2. Say: "Let's discuss AI and machine learning"
3. Chat about the topic
4. Later ask: "What did we discuss about AI?"
5. Should retrieve from Pinecone (episodic memory)

## Troubleshooting:

**"Index already exists" error:**
- Normal on restart, Pinecone reuses existing index

**"Dimension mismatch" error:**
- Delete index in Pinecone dashboard and restart app

**Slow first query:**
- Pinecone cold start, subsequent queries are fast

## Free Tier Limits:

- **1 index** (we use 1: episodic-memory)
- **100K vectors** (plenty for conversations)
- **2GB storage**
- **Unlimited queries**

## Next Steps (Phase 3):

- Add Neo4j for semantic memory (facts)
- NeonDB becomes optional
- Full separation of memory types

---

**Phase 2 Status:** Ready to test
**Estimated Time:** 10 minutes setup + testing
