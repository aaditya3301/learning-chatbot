# Auto-Learning Chatbot

A smart chatbot that automatically learns from conversations using Groq AI and NeonDB (PostgreSQL with pgvector).

## Features
- Automatic learning from conversations
- Persistent memory using NeonDB
- Retrieves relevant information when needed
- Powered by Llama 3.3 70B via Groq

## Setup

### 1. Get API Keys (Both FREE!)

**Groq API Key:**
- Go to https://console.groq.com
- Sign up and create an API key

**NeonDB Connection String:**
- Go to https://neon.tech
- Create a free account
- Create a new project
- Copy the connection string (looks like: `postgresql://user:password@host/dbname`)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

Add your keys to `app.py` or use Streamlit secrets (recommended for deployment)

### 4. Run Locally

```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo
4. In "Advanced settings" → "Secrets", add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   NEON_CONNECTION_STRING = "postgresql://user:password@host/dbname"
   ```
5. Click "Deploy"

## Why NeonDB?

- **Persistent Memory**: Your chatbot remembers conversations even after restarts
- **Free Tier**: 0.5 GB storage, plenty for a chatbot
- **Fast**: Built on PostgreSQL with pgvector for efficient similarity search
- **Scalable**: Easy to upgrade if you need more storage
