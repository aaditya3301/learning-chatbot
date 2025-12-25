import streamlit as st
import os

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from neo4j import GraphDatabase

# --- CONFIGURATION ---

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USERNAME = st.secrets["NEO4J_USERNAME"]
    NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    NEO4J_URI = os.getenv("NEO4J_URI", "")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

if not GROQ_API_KEY:
    st.error("⚠️ Please add your Groq API Key")
    st.stop()

if not PINECONE_API_KEY:
    st.error("⚠️ Please add your Pinecone API Key")
    st.stop()

if not NEO4J_URI or not NEO4J_PASSWORD:
    st.error("⚠️ Please add your Neo4j credentials")
    st.stop()

# --- INITIAL SETUP ---
@st.cache_resource
def load_resources():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "episodic-memory"
    
    if index_name not in pc.list_indexes().names():
        pc.create_index(name=index_name, dimension=384, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))
    
    episodic_db = PineconeVectorStore(index_name=index_name, embedding=embedding_model, pinecone_api_key=PINECONE_API_KEY)
    knowledge_graph = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=GROQ_API_KEY)
    
    return episodic_db, knowledge_graph, llm

episodic_db, knowledge_graph, llm = load_resources()

# --- FUNCTIONS ---

def classify_memory(user_message, bot_response):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Classify the conversation type. Return ONLY one word.

EPISODIC - casual chat, greetings, questions about general topics
SEMANTIC - user shares personal facts (name, location, preferences, job, passwords)
BOTH - conversation contains both casual chat AND personal facts
NONE - no meaningful content

Examples:
"Hello" → EPISODIC
"My name is Alex" → SEMANTIC
"My name is Alex and how are you?" → BOTH
"What's 2+2?" → NONE

Return ONLY: EPISODIC or SEMANTIC or BOTH or NONE"""),
        ("human", f"User: {user_message}\nBot: {bot_response}\n\nClassify:")
    ])
    return (prompt | llm).invoke({}).content.strip().upper()

def extract_structured_facts(user_message, bot_response):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract facts as: ENTITY1|RELATIONSHIP|ENTITY2|CONFIDENCE

CONFIDENCE levels:
- HIGH: Direct statement ("I am", "My name is", "I live in")
- MEDIUM: Implied or mentioned casually
- LOW: Uncertain ("I think", "maybe", "probably")

Examples:
"My name is Alex" → User|HAS_NAME|Alex|HIGH
"I live in NYC" → User|LIVES_IN|NYC|HIGH
"I think I like pizza" → User|LIKES|Pizza|LOW
"Maybe I work as engineer" → User|WORKS_AS|Engineer|LOW

One fact per line. Return NONE if no facts."""),
        ("human", f"User: {user_message}\nBot: {bot_response}\n\nExtract:")
    ])
    return (prompt | llm).invoke({}).content.strip()

def detect_correction_keywords(user_message):
    """Detect if user is correcting previous information."""
    correction_keywords = [
        "actually", "no", "correction", "i meant", "i mean",
        "not", "wrong", "mistake", "changed my mind",
        "instead", "rather", "moved to", "now i"
    ]
    message_lower = user_message.lower()
    return any(keyword in message_lower for keyword in correction_keywords)

def filter_emotional_statements(text):
    """Detect if statement is temporary emotion vs stable fact."""
    # Temporary emotions (should NOT be stored as facts)
    temporary_emotions = [
        "i'm happy", "i'm sad", "i'm angry", "i'm frustrated",
        "i'm tired", "i'm excited", "i hate mondays",
        "i'm annoyed", "i'm bored", "feeling"
    ]
    
    # Critical facts (SHOULD be stored even if emotional)
    critical_facts = [
        "allergic", "allergy", "medical", "condition",
        "disease", "medication", "emergency"
    ]
    
    text_lower = text.lower()
    
    # Check if it's a critical fact
    if any(critical in text_lower for critical in critical_facts):
        return False  # Not filtered, should store
    
    # Check if it's temporary emotion
    if any(emotion in text_lower for emotion in temporary_emotions):
        return True  # Filtered, don't store as fact
    
    return False  # Not emotional, can store

def prioritize_fact(entity1, relationship, entity2):
    """Assign priority level to fact."""
    # CRITICAL facts
    critical_patterns = [
        ("HAS_NAME", "CRITICAL"),
        ("HAS_PASSWORD", "CRITICAL"),
        ("ALLERGIC_TO", "CRITICAL"),
        ("HAS_MEDICAL", "CRITICAL"),
        ("EMERGENCY_CONTACT", "CRITICAL")
    ]
    
    # IMPORTANT facts
    important_patterns = [
        ("LIVES_IN", "IMPORTANT"),
        ("WORKS_AS", "IMPORTANT"),
        ("WORKS_AT", "IMPORTANT"),
        ("STUDIED_AT", "IMPORTANT"),
        ("FAMILY_MEMBER", "IMPORTANT")
    ]
    
    # Check patterns
    for pattern, priority in critical_patterns:
        if pattern in relationship.upper():
            return priority
    
    for pattern, priority in important_patterns:
        if pattern in relationship.upper():
            return priority
    
    return "NORMAL"  # Default priority

def validate_fact(entity1, relationship, entity2, confidence):
    """Validate if this is a real fact worth storing."""
    # Only store HIGH and MEDIUM confidence facts
    if confidence not in ["HIGH", "MEDIUM"]:
        return False
    
    # Filter out temporary emotions
    if filter_emotional_statements(f"{entity1} {relationship} {entity2}"):
        return False
    
    # Check if it's an opinion vs fact
    opinion_keywords = ["think", "feel", "believe", "opinion", "maybe", "probably"]
    if any(word in entity2.lower() for word in opinion_keywords):
        return False
    
    return True

def check_contradiction(entity1, relationship, entity2):
    """Check if this fact contradicts existing knowledge."""
    with knowledge_graph.session() as session:
        # Find existing facts with same entity and relationship
        query = """
        MATCH (e1:Entity {name: $entity1})-[r:RELATION {type: $relationship}]->(e2:Entity)
        RETURN e2.name as existing_value
        """
        results = session.run(query, entity1=entity1, relationship=relationship)
        existing = [r["existing_value"] for r in results]
        
        if existing and entity2 not in existing:
            return existing[0]  # Return the contradicting value
        return None

def update_fact_in_graph(entity1, relationship, old_value, new_value, reason="corrected"):
    """Update an existing fact and archive the old one with reason."""
    with knowledge_graph.session() as session:
        # Archive old relationship with reason
        session.run("""
            MATCH (e1:Entity {name: $entity1})-[r:RELATION {type: $relationship}]->(e2:Entity {name: $old_value})
            SET r.archived = true, 
                r.archived_at = datetime(),
                r.archive_reason = $reason
        """, entity1=entity1, relationship=relationship, old_value=old_value, reason=reason)
        
        # Create new relationship
        session.run("""
            MERGE (e1:Entity {name: $entity1})
            MERGE (e2:Entity {name: $new_value})
            MERGE (e1)-[r:RELATION {type: $relationship}]->(e2)
            SET r.timestamp = datetime(), 
                r.updated = true,
                r.previous_value = $old_value
        """, entity1=entity1, relationship=relationship, new_value=new_value, old_value=old_value)

def store_in_knowledge_graph(facts_text, user_message=""):
    if not facts_text or facts_text == "NONE":
        return
    
    facts = [f.strip() for f in facts_text.split("\n") if f.strip() and "|" in f]
    
    if not facts:
        return
    
    # Detect if this is a correction
    is_correction = detect_correction_keywords(user_message)
        
    with knowledge_graph.session() as session:
        for fact in facts:
            try:
                parts = fact.split("|")
                if len(parts) >= 3:
                    e1 = parts[0].strip()
                    rel = parts[1].strip()
                    e2 = parts[2].strip()
                    confidence = parts[3].strip() if len(parts) > 3 else "MEDIUM"
                    
                    # Validate fact
                    if not validate_fact(e1, rel, e2, confidence):
                        continue
                    
                    # Get priority
                    priority = prioritize_fact(e1, rel, e2)
                    
                    # Check for contradictions
                    contradiction = check_contradiction(e1, rel, e2)
                    
                    if contradiction:
                        # Update existing fact
                        reason = "corrected" if is_correction else "updated"
                        update_fact_in_graph(e1, rel, contradiction, e2, reason)
                    else:
                        # Create new fact
                        session.run("""
                            MERGE (e1:Entity {name: $e1})
                            MERGE (e2:Entity {name: $e2})
                            MERGE (e1)-[r:RELATION {type: $rel}]->(e2)
                            SET r.timestamp = datetime(), 
                                r.confidence = $confidence,
                                r.priority = $priority
                        """, e1=e1, e2=e2, rel=rel, confidence=confidence, priority=priority)
            except:
                pass

def query_knowledge_graph(question):
    """Query Neo4j for relevant facts (excluding archived)."""
    prompt = ChatPromptTemplate.from_messages([("system", "Extract main entity from question. Return only entity name."), ("human", question)])
    entity = (prompt | llm).invoke({}).content.strip()
    with knowledge_graph.session() as session:
        # Only get non-archived facts
        results = session.run("""
            MATCH (e1:Entity)-[r:RELATION]->(e2:Entity) 
            WHERE (e1.name CONTAINS $entity OR e2.name CONTAINS $entity)
            AND (r.archived IS NULL OR r.archived = false)
            RETURN e1.name as e1, r.type as rel, e2.name as e2 
            LIMIT 5
        """, entity=entity)
        return [f"{r['e1']} {r['rel']} {r['e2']}" for r in results]

def store_episodic_memory(user_message, bot_response):
    doc = Document(page_content=f"User: {user_message}\nAssistant: {bot_response}", metadata={"memory_type": "episodic"})
    episodic_db.add_documents([doc])

def process_and_store_memory(user_message, bot_response):
    memory_type = classify_memory(user_message, bot_response)
    if memory_type in ["EPISODIC", "BOTH"]:
        store_episodic_memory(user_message, bot_response)
    if memory_type in ["SEMANTIC", "BOTH"]:
        facts = extract_structured_facts(user_message, bot_response)
        store_in_knowledge_graph(facts, user_message)  # Pass user_message for correction detection

def route_query(question):
    """Determine if question needs factual, contextual, or mixed memory."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Analyze the question and classify it. Return ONLY one word.

FACTUAL - asking for specific facts (name, location, preferences, job, etc.)
CONTEXTUAL - asking about past conversations, discussions, what was said
MIXED - needs both facts and conversation context

Examples:
"What's my name?" → FACTUAL
"Where do I live?" → FACTUAL
"What did we discuss yesterday?" → CONTEXTUAL
"What did I tell you about my job?" → CONTEXTUAL
"Tell me about my food preferences" → MIXED
"What do you know about me?" → MIXED

Return ONLY: FACTUAL or CONTEXTUAL or MIXED"""),
        ("human", question)
    ])
    return (prompt | llm).invoke({}).content.strip().upper()

def rank_memories_by_relevance(memories, question):
    """Score and rank memories by relevance to question."""
    if not memories:
        return []
    
    # Simple relevance: check keyword overlap
    question_words = set(question.lower().split())
    scored = []
    
    for mem in memories:
        content = mem.page_content if hasattr(mem, 'page_content') else str(mem)
        content_words = set(content.lower().split())
        overlap = len(question_words & content_words)
        scored.append((mem, overlap))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return [mem for mem, score in scored if score > 0]

def merge_and_deduplicate_context(episodic_memories, semantic_facts):
    """Combine memories intelligently, removing duplicates."""
    context_parts = []
    seen_content = set()
    
    # Add semantic facts first (higher priority)
    if semantic_facts:
        facts_text = "\n".join(semantic_facts)
        if facts_text not in seen_content:
            context_parts.append(f"FACTS ABOUT USER:\n{facts_text}")
            seen_content.add(facts_text)
    
    # Add episodic memories
    if episodic_memories:
        unique_conversations = []
        for mem in episodic_memories:
            content = mem.page_content
            # Check if similar content already added
            if content not in seen_content:
                unique_conversations.append(content)
                seen_content.add(content)
        
        if unique_conversations:
            context_parts.append(f"PAST CONVERSATIONS:\n" + "\n\n".join(unique_conversations))
    
    return "\n\n".join(context_parts) if context_parts else None

def ask_bot(question):
    """Smart chatbot with query routing and optimized retrieval."""
    # 1. Route the query
    query_type = route_query(question)
    
    episodic_memories = []
    semantic_facts = []
    
    # 2. Fetch based on query type
    if query_type in ["FACTUAL", "MIXED"]:
        semantic_facts = query_knowledge_graph(question)
    
    if query_type in ["CONTEXTUAL", "MIXED"]:
        results = episodic_db.similarity_search_with_score(question, k=3)
        episodic_memories = [doc for doc, score in results if score < 0.7]
        # Rank by relevance
        episodic_memories = rank_memories_by_relevance(episodic_memories, question)
    
    # 3. Build optimized context
    context = merge_and_deduplicate_context(episodic_memories, semantic_facts)
    
    # 4. Generate response
    if context:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"Use this memory to answer:\n\n{context}\n\nAnswer naturally and conversationally."),
            ("human", "{input}")
        ])
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer naturally using your general knowledge."),
            ("human", "{input}")
        ])
    
    return (prompt | llm).invoke({"input": question}).content

# --- UI ---

st.title("Chatbot")

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
        with st.spinner("Thinking..."):
            response = ask_bot(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            process_and_store_memory(prompt, response)
