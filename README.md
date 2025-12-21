# Chatbot

A chatbot that automatically learns from conversations using Groq AI and NeonDB (PostgreSQL with pgvector).

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
