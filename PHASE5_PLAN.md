# Phase 5: Hybrid Retrieval System

## Goal:
Improve how the bot decides WHEN to use episodic vs semantic memory, and how to combine them intelligently.

## Current Issues:

1. **Always queries both** - even when only one is needed
2. **No query routing** - doesn't analyze question type first
3. **Simple context merging** - just concatenates results
4. **No relevance ranking** - treats all memories equally

## What We're Adding:

### 1. **Query Router**
Analyze the question and decide:
- **Factual question** → prioritize Knowledge Graph
- **Contextual question** → prioritize Episodic Memory
- **Mixed question** → use both equally

Examples:
- "What's my name?" → FACTUAL (Neo4j only)
- "What did we discuss yesterday?" → CONTEXTUAL (Pinecone only)
- "Tell me about my food preferences" → MIXED (both)

### 2. **Smart Context Builder**
- Remove duplicate information
- Rank by relevance
- Prioritize recent over old
- Combine related facts

### 3. **Relevance Scoring**
- Score each memory by relevance to question
- Only include high-scoring memories
- Avoid information overload

### 4. **Query Optimization**
- Don't query databases unnecessarily
- Cache frequent queries
- Faster response times

## Implementation:

```python
# New functions:
route_query(question) → "FACTUAL" | "CONTEXTUAL" | "MIXED"
rank_memories(memories, question) → sorted by relevance
merge_context(episodic, semantic) → deduplicated, ranked context
optimize_retrieval(question, query_type) → smart fetching
```

## Example Flows:

### Factual Question:
```
"What's my name?"
    ↓
Route: FACTUAL
    ↓
Query: Neo4j only (skip Pinecone)
    ↓
Result: "Alexander"
```

### Contextual Question:
```
"What did we talk about earlier?"
    ↓
Route: CONTEXTUAL
    ↓
Query: Pinecone only (skip Neo4j)
    ↓
Result: Past conversations
```

### Mixed Question:
```
"What do I like to eat?"
    ↓
Route: MIXED
    ↓
Query: Both databases
    ↓
Merge: Facts (User LIKES Pizza) + Conversations (discussed food)
    ↓
Result: Combined, ranked answer
```

## Benefits:

✅ Faster responses (skip unnecessary queries)
✅ More relevant answers (better context)
✅ Less token usage (smaller prompts)
✅ Smarter retrieval (right memory for right question)

Ready to implement?
