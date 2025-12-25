# Memory Architecture Migration - Phase Breakdown

## PHASE 1: Separate Memory Types (Conceptual Refactor)
**Duration:** 1-2 days  
**Complexity:** Low  
**Goal:** Change how we think about and categorize memory

### What Happens:
1. **Identify two memory types in current system:**
   - **Episodic Memory:** Conversations, context, "what we talked about"
   - **Semantic Memory:** Facts, preferences, truths, "what I know about you"

2. **Refactor code structure:**
   - Create two separate functions: `store_episodic()` and `store_semantic()`
   - Both still use NeonDB, but logically separated
   - Add metadata tags: `memory_type: "episodic"` or `memory_type: "semantic"`

3. **Update extraction logic:**
   - After each message, classify: "Is this a fact or just conversation?"
   - Facts → semantic memory
   - Context → episodic memory

### What Changes in Code:
- Split `extract_and_store_info()` into two functions
- Add classification logic (LLM decides: fact vs conversation)
- Tag all stored data with memory type

### What Stays Same:
- Still using NeonDB/pgvector
- No new infrastructure
- User experience unchanged

### Success Criteria:
✅ Can distinguish between "Alex said he likes pizza" (episodic) vs "Alex likes pizza" (semantic)
✅ Data is tagged correctly
✅ Retrieval can filter by memory type

---

## PHASE 2: Migrate to Dedicated Vector DB
**Duration:** 2-3 days  
**Complexity:** Medium  
**Goal:** Move episodic memory from NeonDB to proper Vector DB

### What Happens:
1. **Choose Vector DB:**
   - **Pinecone** (easiest, free tier: 1 index, 100K vectors)
   - **Weaviate** (more features, self-host or cloud)
   - **Qdrant** (good for self-hosting)

2. **Set up new Vector DB:**
   - Create account
   - Get API key
   - Create index/collection for "episodic_memory"

3. **Migrate episodic data:**
   - Export episodic memories from NeonDB
   - Import to new Vector DB
   - Test retrieval works

4. **Update code:**
   - Replace NeonDB connection for episodic queries
   - Keep NeonDB for semantic (temporary)

### What Changes in Code:
- New imports: `pinecone` or `weaviate-client`
- `store_episodic()` → writes to Vector DB
- `retrieve_episodic()` → reads from Vector DB
- `store_semantic()` → still writes to NeonDB (for now)

### What Stays Same:
- Semantic memory still in NeonDB
- User experience unchanged
- Same LLM (Groq)

### Success Criteria:
✅ Episodic memories stored in Vector DB
✅ Retrieval works correctly
✅ No data loss during migration
✅ Semantic memories still in NeonDB

---

## PHASE 3: Introduce Knowledge Graph
**Duration:** 2-3 days  
**Complexity:** Medium-High  
**Goal:** Add Neo4j for semantic/factual memory

### What Happens:
1. **Set up Neo4j:**
   - Create Neo4j Aura account (free tier)
   - Get connection string
   - Learn basic Cypher queries

2. **Design initial schema:**
   ```
   Nodes:
   - User (properties: name, id)
   - Preference (properties: category, value)
   - Location (properties: city, country)
   - Topic (properties: name)
   
   Relationships:
   - (User)-[:LIKES]->(Preference)
   - (User)-[:LIVES_IN]->(Location)
   - (User)-[:INTERESTED_IN]->(Topic)
   ```

3. **Create graph operations:**
   - `add_fact()` - adds nodes and relationships
   - `update_fact()` - modifies existing facts
   - `query_facts()` - retrieves from graph

4. **Keep both systems running:**
   - Vector DB: episodic memory
   - Neo4j: semantic memory (new)
   - NeonDB: deprecated but still there

### What Changes in Code:
- New imports: `neo4j` driver
- `store_semantic()` → writes to Neo4j (not NeonDB)
- New function: `query_knowledge_graph()`
- Graph connection setup

### What Stays Same:
- Episodic memory in Vector DB
- User experience unchanged
- Same LLM

### Success Criteria:
✅ Neo4j connected and working
✅ Can store facts as nodes/relationships
✅ Can query facts from graph
✅ Both Vector DB and Neo4j working together

---

## PHASE 4: Build Memory Extraction Layer
**Duration:** 3-5 days  
**Complexity:** High  
**Goal:** Automatically extract structured facts from conversations

### What Happens:
1. **Create extraction pipeline:**
   ```
   User message
   ↓
   LLM analyzes
   ↓
   Extracts entities & relationships
   ↓
   Validates (is this a fact?)
   ↓
   Stores in Knowledge Graph
   ```

2. **Build extraction prompts:**
   - Prompt 1: "Extract entities (people, places, things)"
   - Prompt 2: "Extract relationships between entities"
   - Prompt 3: "Validate: is this a fact or opinion?"

3. **Implement validation:**
   - Check if fact contradicts existing knowledge
   - Ask for confirmation if uncertain
   - Confidence scoring

4. **Handle updates:**
   - If new fact contradicts old fact → update graph
   - Keep history of changes

### What Changes in Code:
- New function: `extract_structured_facts(message)`
- New function: `validate_fact(fact)`
- New function: `update_or_create_in_graph(fact)`
- Complex LLM prompting logic

### What Stays Same:
- Vector DB for episodic
- Neo4j for semantic
- User can still chat normally

### Success Criteria:
✅ "I live in NYC" → creates (User)-[:LIVES_IN]->(NYC)
✅ "I love pizza" → creates (User)-[:LIKES]->(Pizza)
✅ Facts are validated before storing
✅ Contradictions are handled

---

## PHASE 5: Hybrid Retrieval System
**Duration:** 2-3 days  
**Complexity:** Medium  
**Goal:** Combine Vector DB + Knowledge Graph for answers

### What Happens:
1. **Build new retrieval flow:**
   ```
   User question
   ↓
   Parallel queries:
   - Vector DB → "similar conversations"
   - Knowledge Graph → "verified facts"
   ↓
   Combine results
   ↓
   LLM generates answer using both
   ```

2. **Implement query router:**
   - Analyze question type
   - Factual question? → prioritize Knowledge Graph
   - Contextual question? → prioritize Vector DB
   - Mixed? → use both equally

3. **Create context builder:**
   - Merge episodic + semantic memories
   - Remove duplicates
   - Rank by relevance

### What Changes in Code:
- New function: `hybrid_retrieve(question)`
- New function: `route_query(question)`
- New function: `merge_memories(episodic, semantic)`
- Updated `ask_bot()` to use hybrid retrieval

### What Stays Same:
- Same databases
- User experience (but better answers)

### Success Criteria:
✅ "What's my name?" → queries Knowledge Graph
✅ "What did we discuss yesterday?" → queries Vector DB
✅ "Tell me about my food preferences" → queries both
✅ Answers are more accurate

---

## PHASE 6: Define Storage Rules
**Duration:** 1-2 days  
**Complexity:** Low  
**Goal:** Clear rules for what goes where

### What Happens:
1. **Create decision matrix:**
   ```
   Vector DB stores:
   ✓ Full conversation messages
   ✓ Summaries of discussions
   ✓ Contextual insights
   ✓ Temporary thoughts
   ✓ Emotional statements
   
   Knowledge Graph stores:
   ✓ User facts (name, age, location)
   ✓ Preferences (likes, dislikes)
   ✓ Relationships (knows, works_with)
   ✓ Stable truths
   ✓ Skills, tools, interests
   ```

2. **Implement classification:**
   - LLM classifies each piece of info
   - Routes to correct storage

3. **Add metadata:**
   - Timestamp
   - Confidence score
   - Source (user said vs inferred)

### What Changes in Code:
- New function: `classify_memory_type(text)`
- Updated storage logic with strict rules
- Better metadata tracking

### Success Criteria:
✅ No facts stored as embeddings only
✅ No raw chat in Knowledge Graph
✅ Clear separation maintained

---

## PHASE 7: Memory Update Rules
**Duration:** 3-4 days  
**Complexity:** High  
**Goal:** Smart memory management (updates, corrections, decay)

### What Happens:
1. **Implement correction handling:**
   ```
   User: "Actually, I live in LA, not NYC"
   ↓
   Detect contradiction
   ↓
   Update graph: (User)-[:LIVES_IN]->(LA)
   ↓
   Archive old fact with timestamp
   ```

2. **Add confidence decay:**
   - Facts not mentioned in 6 months → lower confidence
   - Very old facts → marked as "needs verification"

3. **Emotional filtering:**
   - "I hate Mondays" → episodic only (temporary feeling)
   - "I'm allergic to peanuts" → semantic (important fact)

4. **Conflict resolution:**
   - If two facts contradict → ask user
   - Keep history of all changes

### What Changes in Code:
- New function: `detect_contradiction(new_fact, existing_facts)`
- New function: `update_fact_with_history(fact)`
- New function: `decay_confidence()`
- Scheduled job for confidence decay

### Success Criteria:
✅ User can correct facts
✅ Old facts decay over time
✅ Contradictions are detected
✅ Emotional statements don't become "facts"

---

## PHASE 8: Deprecate NeonDB
**Duration:** 1 day  
**Complexity:** Low  
**Goal:** Clean up, remove old infrastructure

### What Happens:
1. **Verify migration complete:**
   - All episodic → Vector DB ✓
   - All semantic → Neo4j ✓
   - NeonDB empty or unused

2. **Optional: Keep NeonDB for:**
   - User authentication
   - App logs
   - Configuration settings
   - Non-memory data

3. **Update deployment:**
   - Remove NeonDB from requirements (if fully deprecated)
   - Update environment variables
   - Clean up old code

### What Changes in Code:
- Remove NeonDB connection (if not needed)
- Clean up old functions
- Update documentation

### Success Criteria:
✅ System works without NeonDB
✅ All memory in Vector DB + Neo4j
✅ Cleaner architecture

---

## Final Architecture:

```
User Input
    ↓
┌───────────────────────────────┐
│   Groq LLM (Orchestrator)    │
└───────────────────────────────┘
    ↓                    ↓
┌─────────────┐    ┌──────────────┐
│  Vector DB  │    │ Knowledge    │
│  (Pinecone) │    │ Graph (Neo4j)│
│             │    │              │
│ Episodic    │    │ Semantic     │
│ Memory      │    │ Memory       │
└─────────────┘    └──────────────┘
```

---

## Timeline Summary:
- **Phase 1:** 1-2 days
- **Phase 2:** 2-3 days
- **Phase 3:** 2-3 days
- **Phase 4:** 3-5 days
- **Phase 5:** 2-3 days
- **Phase 6:** 1-2 days
- **Phase 7:** 3-4 days
- **Phase 8:** 1 day

**Total:** ~15-23 days (3-4 weeks)

---

## Cost Breakdown (Free Tiers):
- **Pinecone:** Free (1 index, 100K vectors)
- **Neo4j Aura:** Free (50MB storage)
- **Groq:** Free (generous limits)
- **Total:** $0/month

---

## Risk Assessment:
- **Low Risk:** Phases 1, 6, 8
- **Medium Risk:** Phases 2, 3, 5
- **High Risk:** Phases 4, 7 (complex logic)

---

## Recommendation:
Start with **Phases 1-3** this week. Get the infrastructure right. Then tackle the complex extraction logic (Phase 4) next week.
