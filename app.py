import streamlit as st
import os

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# --- CONFIGURATION ---

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    NEON_CONNECTION_STRING = st.secrets["NEON_CONNECTION_STRING"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    NEON_CONNECTION_STRING = os.getenv("NEON_CONNECTION_STRING", "")

if not GROQ_API_KEY:
    st.error("⚠️ Please add your Groq API Key. Get one free at https://console.groq.com")
    st.stop()

if not NEON_CONNECTION_STRING:
    st.error("⚠️ Please add your NeonDB connection string. Get one free at https://neon.tech")
    st.stop()

# --- INITIAL SETUP ---
@st.cache_resource
def load_resources():
    # 1. Embedding Model
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # 2. Vector Database
    vectordb = PGVector(
        connection=NEON_CONNECTION_STRING,
        embeddings=embedding_model,
        collection_name="chatbot_memory",
        use_jsonb=True
    )
    
    # 3. Chat Model
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=GROQ_API_KEY
    )
    
    return vectordb, llm

if GROQ_API_KEY and NEON_CONNECTION_STRING:
    vectordb, llm = load_resources()

# --- FUNCTIONS ---

def extract_and_store_info(user_message, bot_response):
    """Automatically detect and store important information from conversation."""
    # Use LLM to extract key facts worth remembering
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an information extractor. Analyze the conversation and extract ONLY specific, factual information worth remembering (like names, preferences, facts, passwords, personal details, etc.).

Return ONLY the extracted facts in a clear, concise format. If there's nothing specific to remember, return "NONE".

Examples:
- "My name is John" → "User's name is John"
- "The password is abc123" → "Password: abc123"
- "I love pizza" → "User loves pizza"
- "Hello" → "NONE"
- "What's the weather?" → "NONE"
"""),
        ("human", f"User said: {user_message}\nBot replied: {bot_response}\n\nExtract key facts:")
    ])
    
    chain = extraction_prompt | llm
    result = chain.invoke({})
    extracted = result.content.strip()
    
    # Store if we found something meaningful
    if extracted and extracted != "NONE" and len(extracted) > 5:
        doc = Document(
            page_content=extracted,
            metadata={"source": "auto_learned", "user_msg": user_message[:100]}
        )
        vectordb.add_documents([doc])
        return True
    return False

def ask_bot(question):
    """Smart chatbot that uses memory when relevant, otherwise chats normally."""
    # 1. Search memory for relevant context
    docs = vectordb.similarity_search_with_score(question, k=2)
    
    # 2. Check if we found relevant memory (score < 0.7 means good match)
    relevant_docs = [doc for doc, score in docs if score < 0.7]
    
    # 3. If we have relevant memory, use it
    if relevant_docs:
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a helpful AI assistant. Use the following information from your memory if it's relevant to answer the question:\n\n{context}\n\nIf the memory is relevant, use it. Otherwise, answer normally using your general knowledge."),
            ("human", "{input}")
        ])
    else:
        # 4. No relevant memory, just chat normally
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Answer questions naturally and conversationally."),
            ("human", "{input}")
        ])
    
    # 5. Generate response
    chain = prompt | llm
    response = chain.invoke({"input": question})
    return response.content

# --- USER INTERFACE ---

st.title("Chatbot")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "llm" in globals():
            with st.spinner("Thinking..."):
                response = ask_bot(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Auto-learn from this conversation (silently)
                extract_and_store_info(prompt, response)
        else:
            st.error("System not loaded. Check API Key.")