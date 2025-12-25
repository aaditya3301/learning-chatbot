# Phase 3 Setup - Neo4j Knowledge Graph

## What's Changing:

**Semantic Memory:** NeonDB → **Neo4j** (Knowledge Graph)
**Episodic Memory:** Still in Pinecone

## Setup Steps:

### 1. Create Neo4j Aura Account

1. Go to https://neo4j.com/cloud/aura/
2. Click "Start Free"
3. Sign up with email or Google
4. Create a new instance:
   - Select "AuraDB Free"
   - Name it (e.g., "chatbot-memory")
   - Click "Create"

### 2. Get Credentials

After instance is created:
1. **Download credentials** (important - save the password!)
2. You'll get:
   - **URI:** `neo4j+s://xxxxx.databases.neo4j.io`
   - **Username:** `neo4j`
   - **Password:** (the one you saved)

### 3. Add to Secrets

Open `.streamlit/secrets.toml` and update:
```toml
NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_actual_password"
```

### 4. Install Neo4j Driver

```bash
pip install neo4j
```

Or:
```bash
pip install -r requirements.txt
```

### 5. Run the App

```bash
streamlit run app.py
```

## How It Works:

### Facts are stored as Graph:

**Input:** "My name is Alex and I live in NYC"

**Extracted:**
```
User|HAS_NAME|Alex
User|LIVES_IN|NYC
```

**Stored in Neo4j as:**
```
(User)-[:HAS_NAME]->(Alex)
(User)-[:LIVES_IN]->(NYC)
```

### Querying:

**Question:** "What's my name?"

**Neo4j Query:**
```cypher
MATCH (User)-[:HAS_NAME]->(name)
RETURN name
```

**Result:** "Alex"

## Architecture Now:

```
User Input
    ↓
Groq LLM
    ↓
┌─────────────────┐    ┌──────────────┐
│   Pinecone      │    │   Neo4j      │
│   (Episodic)    │    │  (Semantic)  │
│                 │    │              │
│ Conversations   │    │   Facts as   │
│ Context         │    │   Graph      │
└─────────────────┘    └──────────────┘
```

## Benefits of Knowledge Graph:

✅ **Structured Facts** - Clear relationships
✅ **Queryable** - "Who likes what?"
✅ **Updatable** - Easy to correct facts
✅ **Explainable** - See why it knows something
✅ **Relationship Queries** - "What's connected to Alex?"

## Example Relationships:

```
(User)-[:HAS_NAME]->(Alex)
(User)-[:LIVES_IN]->(NYC)
(User)-[:LIKES]->(Pizza)
(User)-[:WORKS_AS]->(Engineer)
(WiFi)-[:HAS_PASSWORD]->(abc123)
```

## Testing:

1. Say: "My name is Alex, I live in NYC, and I love pizza"
2. Check Neo4j Browser (in Aura dashboard)
3. Run query: `MATCH (n)-[r]->(m) RETURN n,r,m`
4. You should see the graph!
5. Ask bot: "What's my name?" → Should query graph

## Neo4j Browser:

Access it from your Aura dashboard:
- Click "Open" on your instance
- Use Neo4j Browser to visualize your knowledge graph
- Run Cypher queries to explore data

## Free Tier Limits:

- **50MB storage** (plenty for personal facts)
- **Unlimited queries**
- **1 database**
- **Always on** (no sleeping)

## Troubleshooting:

**Connection error:**
- Check URI format: `neo4j+s://` (with the `+s`)
- Verify password is correct
- Instance must be "Running" in Aura dashboard

**No facts stored:**
- Check extraction is working (LLM might return "NONE")
- Verify Neo4j connection in app logs

**Query returns nothing:**
- Graph might be empty
- Check Neo4j Browser to see stored data

## Next Steps (Phase 4):

- Improve fact extraction
- Add validation before storing
- Handle contradictions
- Build smarter extraction prompts

---

**Phase 3 Status:** Ready to test
**Estimated Time:** 15 minutes setup + testing
