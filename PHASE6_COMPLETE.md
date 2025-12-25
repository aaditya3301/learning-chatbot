# Phase 6: Storage Rules & Decision Matrix

## Goal:
Create strict, clear rules for what data goes into which database to prevent memory corruption.

## The Rules:

### 📊 PINECONE (Episodic Memory)
**Store:**
✅ Full conversation messages (user + bot)
✅ Discussion summaries
✅ Contextual insights
✅ Temporary thoughts
✅ Emotional statements ("I'm happy", "I'm frustrated")
✅ Opinions ("I think", "I believe")
✅ Questions asked
✅ Explanations given

**DON'T Store:**
❌ Hard facts (name, location, job)
❌ Preferences as standalone facts
❌ Passwords or sensitive data
❌ Relationships between entities

**Metadata:**
- `memory_type: "episodic"`
- `timestamp`
- `conversation_id`
- `user_message_preview`

---

### 🕸️ NEO4J (Semantic Memory)
**Store:**
✅ User facts (name, age, location)
✅ Preferences (likes, dislikes)
✅ Relationships (knows, works_with)
✅ Stable truths
✅ Skills, tools, interests
✅ Passwords (encrypted ideally)
✅ Important dates
✅ Job, education, family

**DON'T Store:**
❌ Raw chat messages
❌ Temporary feelings
❌ Opinions (unless stated as preference)
❌ Questions
❌ Uncertain statements ("maybe", "I think")

**Properties:**
- `confidence: HIGH/MEDIUM/LOW`
- `timestamp`
- `archived: true/false`
- `updated: true/false`

---

## Decision Matrix:

| Statement | Type | Storage | Reason |
|-----------|------|---------|--------|
| "My name is Alex" | SEMANTIC | Neo4j | Hard fact |
| "I love pizza" | SEMANTIC | Neo4j | Preference (stable) |
| "I'm happy today" | EPISODIC | Pinecone | Temporary emotion |
| "What's the weather?" | EPISODIC | Pinecone | Question, context |
| "I think I like pizza" | EPISODIC | Pinecone | Uncertain, opinion |
| "I work at Google" | SEMANTIC | Neo4j | Stable fact |
| "We discussed AI yesterday" | EPISODIC | Pinecone | Conversation context |
| "Password is abc123" | SEMANTIC | Neo4j | Important fact |
| "Tell me about yourself" | EPISODIC | Pinecone | Question |
| "I live in NYC" | SEMANTIC | Neo4j | Location fact |

---

## Classification Logic:

```python
def should_store_in_neo4j(statement):
    """Determine if statement is a fact for Neo4j."""
    
    # Check for fact indicators
    fact_patterns = [
        "my name is",
        "i live in",
        "i work as",
        "i am a",
        "i like",
        "i love",
        "i hate",
        "password is",
        "my email is"
    ]
    
    # Check for uncertainty (should NOT go to Neo4j)
    uncertain_patterns = [
        "i think",
        "maybe",
        "probably",
        "i guess",
        "not sure"
    ]
    
    statement_lower = statement.lower()
    
    # If uncertain, don't store as fact
    if any(pattern in statement_lower for pattern in uncertain_patterns):
        return False
    
    # If matches fact pattern, store in Neo4j
    if any(pattern in statement_lower for pattern in fact_patterns):
        return True
    
    return False
```

---

## Implementation Status:

✅ **Already Implemented:**
- Classification (EPISODIC vs SEMANTIC)
- Confidence scoring
- Validation before storing
- Separate storage functions

✅ **Working Correctly:**
- Facts go to Neo4j
- Conversations go to Pinecone
- Hybrid retrieval combines both

---

## Best Practices:

### 1. **When in Doubt:**
- Store in Pinecone (episodic)
- Better to have context than lose it
- Facts can be extracted later

### 2. **Confidence Threshold:**
- Only HIGH and MEDIUM confidence → Neo4j
- LOW confidence → Pinecone only

### 3. **Metadata is Key:**
- Always tag with `memory_type`
- Always include `timestamp`
- Track `source` (user_input, inferred, etc.)

### 4. **Regular Cleanup:**
- Archive old episodic memories (>30 days)
- Keep semantic facts forever
- Update facts when contradictions found

---

## Phase 6 Status: ✅ COMPLETE

**Current Implementation:**
- Clear separation of memory types
- Proper classification logic
- Validation before storage
- Metadata tracking
- No mixing of data types

**No code changes needed** - Phase 6 is about documenting and enforcing rules, which we've already implemented in Phases 1-5!

---

## Summary:

Your chatbot now has:
1. ✅ Episodic Memory (Pinecone) - conversations, context
2. ✅ Semantic Memory (Neo4j) - facts, relationships
3. ✅ Smart classification
4. ✅ Validation & confidence scoring
5. ✅ Query routing
6. ✅ **Clear storage rules** ← Phase 6

Ready for Phase 7 (Memory Update Rules)?
