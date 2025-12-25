# Phase 4: Memory Extraction Layer

## Goal:
Build intelligent fact extraction with validation to prevent:
- Contradictions
- Hallucinated memories
- Opinion stored as fact
- Incorrect updates

## What We're Adding:

### 1. **Fact Validation**
Before storing, check:
- Is this actually a fact or opinion?
- Does it contradict existing knowledge?
- Is the confidence high enough?

### 2. **Contradiction Detection**
```
Existing: User LIVES_IN NYC
New: User LIVES_IN LA
→ Detect contradiction
→ Update old fact
→ Keep history
```

### 3. **Confidence Scoring**
- "I live in NYC" → High confidence (direct statement)
- "I think I live in NYC" → Low confidence (uncertain)
- "Maybe NYC" → Very low confidence (guess)

### 4. **Fact Types**
Classify facts by importance:
- **Critical**: Name, passwords, allergies
- **Important**: Location, job, preferences
- **Normal**: Interests, hobbies

### 5. **Update vs Create**
- Check if fact already exists
- If exists → update with new value
- Keep timestamp of changes

## Implementation:

```python
# New functions:
validate_fact(fact) → True/False + confidence score
check_contradiction(new_fact, existing_facts) → contradiction or None
update_or_create_fact(fact) → updates if exists, creates if new
get_fact_history(entity, relationship) → shows all changes over time
```

## Example Flow:

```
User: "My name is Alex"
    ↓
Extract: User|HAS_NAME|Alex
    ↓
Validate: ✓ High confidence, direct statement
    ↓
Check contradictions: None found
    ↓
Store in Neo4j
```

Later:
```
User: "Actually, my name is Alexander"
    ↓
Extract: User|HAS_NAME|Alexander
    ↓
Validate: ✓ High confidence
    ↓
Check contradictions: Found! User|HAS_NAME|Alex
    ↓
Update: Alex → Alexander (keep history)
    ↓
Store update
```

## Benefits:

✅ No contradictory facts
✅ Can correct mistakes
✅ Tracks changes over time
✅ Filters out opinions/guesses
✅ More reliable memory

Ready to implement?
