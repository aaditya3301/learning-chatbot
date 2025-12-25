# Phase 7: Memory Update Rules

## Goal:
Add intelligent memory management - corrections, confidence decay, and emotional filtering.

## What We're Adding:

### 1. **Correction Detection**
Detect when user corrects themselves:
- "Actually, I live in LA" (correcting previous "NYC")
- "No, my name is Alexander" (correcting "Alex")
- "I changed my mind, I don't like pizza"

### 2. **Confidence Decay**
Facts get less confident over time:
- Facts not mentioned in 30 days → confidence drops
- Facts not mentioned in 90 days → marked "needs_verification"
- Very old facts → archived automatically

### 3. **Emotional Filtering**
Don't store temporary emotions as facts:
- "I hate Mondays" → episodic only (temporary feeling)
- "I'm allergic to peanuts" → semantic (important fact)
- "I'm frustrated" → episodic only
- "I love pizza" → semantic (stable preference)

### 4. **Fact Priority Levels**
```
CRITICAL - name, passwords, allergies, medical info
IMPORTANT - location, job, family, education
NORMAL - preferences, hobbies, interests
LOW - temporary opinions, casual mentions
```

### 5. **Update History**
Track all changes:
- Original value
- New value
- Timestamp of change
- Reason (correction, update, decay)

## Implementation:

```python
# New functions:
detect_correction(new_fact, user_message) → True/False
apply_confidence_decay() → updates old facts
filter_emotional_statements(text) → removes temporary emotions
prioritize_fact(fact) → CRITICAL/IMPORTANT/NORMAL/LOW
get_update_history(entity, relationship) → all changes
```

## Examples:

### Correction:
```
User: "I live in NYC"
→ Stored: User LIVES_IN NYC

User: "Actually, I moved to LA"
→ Detected: Correction keyword "actually"
→ Updated: User LIVES_IN LA
→ Archived: User LIVES_IN NYC (with reason: "corrected")
```

### Confidence Decay:
```
Day 1: User LIKES Pizza (confidence: HIGH)
Day 30: Not mentioned → confidence: MEDIUM
Day 90: Not mentioned → confidence: LOW, needs_verification: true
Day 180: Not mentioned → archived
```

### Emotional Filtering:
```
"I hate Mondays" 
→ Detected: Temporary emotion
→ Stored: Pinecone only (episodic)
→ NOT stored in Neo4j

"I'm allergic to peanuts"
→ Detected: Critical medical fact
→ Stored: Neo4j (semantic)
→ Priority: CRITICAL
```

## Benefits:

✅ Self-correcting memory
✅ Facts stay fresh and relevant
✅ No temporary emotions stored as facts
✅ Critical facts prioritized
✅ Complete audit trail

Ready to implement?
