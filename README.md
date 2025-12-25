# Auto-Learning Chatbot

A chatbot with persistent memory using Pinecone (episodic) and Neo4j (semantic) knowledge graph.

## 🎯 Features

- **Dual Memory System**: Episodic (conversations) + Semantic (facts)
- **Auto-Learning**: Extracts and stores facts automatically
- **Smart Retrieval**: Routes queries to appropriate memory type
- **Contradiction Detection**: Updates facts when corrected
- **Confidence Scoring**: Validates facts before storing
- **Emotional Filtering**: Separates temporary emotions from stable facts
- **Priority Levels**: CRITICAL, IMPORTANT, NORMAL facts
- **Update History**: Complete audit trail of changes

## 🏗️ Architecture

```
User Input → Groq LLM (Llama 3.3 70B)
                ↓
    ┌───────────────────┐    ┌──────────────────┐
    │   Pinecone        │    │   Neo4j          │
    │   (Episodic)      │    │   (Semantic)     │
    │                   │    │                  │
    │ • Conversations   │    │ • Facts as Graph │
    │ • Context         │    │ • Relationships  │
    │ • Questions       │    │ • Priority       │
    └───────────────────┘    └──────────────────┘
```

## 🚀 Quick Start

### 1. Get API Keys (All FREE)

**Groq**: https://console.groq.com
**Pinecone**: https://www.pinecone.io  
**Neo4j**: https://neo4j.com/cloud/aura/

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Secrets

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_key"
PINECONE_API_KEY = "your_pinecone_key"
NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_neo4j_password"
```

### 4. Run

```bash
streamlit run app.py
```

## 💡 How It Works

### Memory Classification
- **Episodic**: "Hello", "What did we discuss?", casual chat
- **Semantic**: "My name is Alex", "I live in NYC", facts
- **Both**: "My name is Alex and how are you?"

### Fact Extraction
```
User: "My name is Alex and I live in NYC"
    ↓
Extracts: 
- User|HAS_NAME|Alex|HIGH
- User|LIVES_IN|NYC|HIGH
    ↓
Stores in Neo4j as graph relationships
```

### Query Routing
```
"What's my name?" → FACTUAL → Neo4j only
"What did we discuss?" → CONTEXTUAL → Pinecone only
"Tell me about me" → MIXED → Both databases
```

### Contradiction Handling
```
User: "I live in NYC"
Later: "Actually, I moved to LA"
    ↓
Detects contradiction
Archives: NYC (reason: "corrected")
Creates: LA (with previous_value: "NYC")
```

## 📊 Cost (Free Tier)

- **Groq**: FREE (generous rate limits)
- **Pinecone**: FREE (100K vectors, 1 index)
- **Neo4j Aura**: FREE (50MB storage)
- **Streamlit Cloud**: FREE (1 public app)

**Total: $0/month**

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo
4. Add secrets in Advanced settings
5. Deploy!

## 🎓 What You Built

This is a **production-grade memory system** using the same architecture as:
- Personal AI assistants
- Enterprise copilots  
- Autonomous agents
- Advanced chatbots

## 🔧 Tech Stack

- **LLM**: Groq (Llama 3.3 70B)
- **Embeddings**: HuggingFace (sentence-transformers)
- **Vector DB**: Pinecone
- **Graph DB**: Neo4j
- **Framework**: LangChain
- **UI**: Streamlit

## 📝 License

MIT
