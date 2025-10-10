# Chat System Configuration Guide

## Overview

The chat system uses a **session-based architecture** where each chat maintains its own isolated conversation history. Messages from different chats never mix.

---

## Architecture

```bash
User → Frontend → Backend API → Database
```


### Key Components:

1. **Chat Sessions** - Isolated conversation containers
2. **Chat Messages** - Individual user/assistant messages
3. **Conversation Context** - Previous messages sent to LLM
4. **Memory Management** - Limit context window size

---

## Configuration Files

### 1. Backend Chat Route
**File:** `backend/app/api/v1/routes/chat.py`

This is where chat behavior is controlled.

#### Context Window Size

**Location:** Line ~48 in `send_message()` function

```bash
previous_messages = db.query(ChatMessage).filter(
ChatMessage.chat_session_id == chat_session.id
).order_by(ChatMessage.created_at.asc()).limit(20).all() # ← CHANGE THIS
```

**Options:**

| Limit | Context Size | Use Case | Speed | Memory |
|-------|--------------|----------|-------|--------|
| `.limit(5)` | Very Short | Quick responses | Fast | Low |
| `.limit(10)` | Short | Simple conversations | Fast | Low |
| `.limit(20)` | Medium | General use | Medium | Medium |
| `.limit(50)` | Long | Complex discussions | Slow | High |
| `.limit(100)` | Very Long | Deep conversations | Slow | High |
| No limit | Full history | Research/Analysis | Very Slow | Very High |

**Example - Short Memory:**
```bash
.limit(5).all() # Only last 5 messages
```

---

#### System Prompt

**Location:** Line ~66 in `send_message()` function

```bash
system_prompt = request.system_prompt or """You are a helpful AI assistant specializing in data quality and data science.
Use markdown formatting. Answer based on the conversation history provided."""
```

**Customization Options:**

**General Assistant:**
```bash
system_prompt = """You are a helpful AI assistant. Be concise and clear."""
```

**Data Science Expert:**
```bash
system_prompt = """You are an expert data scientist with 20 years of experience.
Provide detailed, technical explanations with code examples.
Use markdown formatting and cite best practices."""
```

**Friendly Tutor:**
```bash
system_prompt = """You are a friendly tutor helping beginners learn data science.
Explain complex concepts simply using analogies.
Encourage questions and provide step-by-step guidance."""
```

**Code-Focused:**
```bash
system_prompt = """You are a coding assistant. Provide working code examples.
Always include comments and error handling. Format code in markdown."""
```

---

### 2. LLM Client Configuration
**File:** `backend/app/services/llm_engine/ollama_client.py`

#### Temperature Setting

**Location:** In `generate()` method

```bash
async def generate(
prompt: str,
system_prompt: str = "",
temperature: float = 0.7, # ← CHANGE THIS
max_tokens: int = 2000
):
```

**Temperature Guide:**

| Value | Creativity | Consistency | Use Case |
|-------|------------|-------------|----------|
| 0.1 - 0.3 | Low | High | Technical docs, code |
| 0.4 - 0.6 | Medium-Low | Good | Data analysis |
| 0.7 - 0.8 | Medium | Balanced | General chat |
| 0.9 - 1.0 | High | Variable | Creative writing |
| 1.0+ | Very High | Low | Brainstorming |

**Example - Deterministic:**
```bash
temperature: float = 0.9 # More varied, creative responses
```

---

#### Max Tokens

**Location:** Same function
```bash
max_tokens: int = 2000 # ← CHANGE THIS
```

**Token Guide:**

| Tokens | ~Words | Use Case |
|--------|--------|----------|
| 500 | ~375 | Short answers |
| 1000 | ~750 | Medium explanations |
| 2000 | ~1500 | Detailed responses |
| 4000 | ~3000 | Long documents |
| 8000+ | ~6000+ | Essays, reports |


**Note:** More tokens = slower response + more memory

---

### 3. Frontend Chat Interface
**File:** `frontend/src/features/chat/ChatInterface.jsx`

#### Auto-scroll Behavior

**Location:** Line ~30
```bash
const scrollToBottom = useCallback(() => {
requestAnimationFrame(() => {
messagesEndRef.current?.scrollIntoView({
behavior: 'smooth', // Change to 'instant' for immediate scroll
block: 'end'
});
});
}, []);
```


**Options:**
- `behavior: 'smooth'` - Animated scroll (default)
- `behavior: 'instant'` - Immediate jump
- `behavior: 'auto'` - Browser decides

---

#### Input Placeholder

**Location:** Line ~430

```bash
placeholder="Ask about data quality, anomalies, or data science..." // ← CHANGE THIS
```

**Examples:**
```bash
placeholder="Type your message..."
placeholder="Ask me anything about your data..."
placeholder="What would you like to know?"
```

---

#### Message Display Limit

To prevent UI lag with long conversations:

**Add this** in `loadChatMessages()` function:

```bash
const loadChatMessages = async (sessionId) => {
try {
const response = await axios.get(
${API_BASE}/sessions/${sessionId}/messages?limit=100, // ← ADD LIMIT
{ headers: getHeaders() }
);
setMessages(response.data);
} catch (error) {
console.error('Failed to load messages:', error);
}
};
```

**Then update backend route** in `chat.py`:

```bash
@router.get("/sessions/{session_id}/messages")
async def get_chat_messages(
session_id: int,
limit: int = 100, # ← ADD THIS
db: Session = Depends(get_db)
):
messages = db.query(ChatMessage).filter(
ChatMessage.chat_session_id == session_id
).order_by(
ChatMessage.created_at.desc() # Most recent first
).limit(limit).all() # ← ADD THIS

text
```
```bash
messages.reverse()  # Reverse to show oldest first

return [...]
```

---

## Environment Variables

**File:** `backend/.env`

# Chat-related settings

* OLLAMA_MODEL=gemma2:2b # Model to use
* OLLAMA_TIMEOUT=120 # Timeout in seconds
* CLEANUP_EMPTY_CHATS_DAYS=7 # Delete empty chats after X days


**Model Options:**
- `gemma2:2b` - Fast, good for general use (1.5GB)
- `llama3.2` - Better quality, slower (4GB)
- `mistral` - Balanced (7GB)
- `phi3` - Fast, small (2GB)
- `qwen2.5` - Multilingual (7GB)

---

## Database Schema

### Chat Sessions Table
```bash
CREATE TABLE chat_sessions (
id INTEGER PRIMARY KEY,
name VARCHAR(255),
created_at TIMESTAMP,
updated_at TIMESTAMP
);
```

### Chat Messages Table
```bash
CREATE TABLE chat_messages (
id INTEGER PRIMARY KEY,
chat_session_id INTEGER,
role VARCHAR(20), -- 'user' or 'assistant'
content TEXT,
created_at TIMESTAMP,
FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(id)
);
```

---

## Performance Tuning

### For Faster Responses:

1. **Reduce context window:**
```bash
.limit(5).all() # Only 5 messages
```

2. **Lower max tokens:**
```bash
max_tokens: int = 500
```

3. **Use smaller model:**
```bash
OLLAMA_MODEL=phi3
```

4. **Reduce temperature:**
```bash
temperature: float = 0.3
```

### For Better Quality:

1. **Increase context window:**
```bash
.limit(50).all() # More context
```

2. **Higher max tokens:**
```bash
max_tokens: int = 4000
```

3. **Use larger model:**
```bash
OLLAMA_MODEL=llama3.2
```

4. **Optimize temperature:**
```bash
temperature: float = 0.7
```

---

## Common Customizations

### 1. Add Message Timestamps

**Frontend - ChatInterface.jsx:**

```bash
<div className="text-xs text-gray-500 mt-1"> {new Date(msg.created_at).toLocaleString()} </div>
```

2. Add Character Count Limit
Frontend - ChatInterface.jsx:

```bash
<input
  maxLength={500}  // Max 500 characters
  value={input}
  onChange={(e) => setInput(e.target.value)}
/>
<p className="text-xs text-gray-500">
  {input.length}/500 characters
</p>
```
3. Add Typing Indicator
Backend - Use streaming response (already implemented in model manager)

4. Export Chat History
Add new route in chat.py:
```bash
@router.get("/sessions/{session_id}/export")
async def export_chat(session_id: int, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).all()
    
    export_text = ""
    for msg in messages:
        export_text += f"{msg.role.upper()}: {msg.content}\n\n"
    
    return {"content": export_text}
```
# Troubleshooting
* Issue: Slow responses
- Solution: Reduce context window and max tokens

* Issue: Model doesn't remember
- Solution: Increase context window limit
 
* Issue: Inconsistent answers
- Solution: Lower temperature (0.3-0.5)

* Issue: Boring responses
- Solution: Increase temperature (0.8-0.9)

* Issue: Chat sessions not isolated
- Solution: Check chat_session_id is being passed correctly


---

## Best Practices

1. ✅ Use **limit(20)** for general conversations
2. ✅ Set **temperature=0.7** for balanced responses
3. ✅ Keep **max_tokens=2000** for detailed answers
4. ✅ Enable **auto-cleanup** for old empty chats
5. ✅ Use **streaming** for better UX with long responses
6. ✅ Test with different models to find best fit
7. ✅ Monitor memory usage with large context windows

---

## Quick Reference

| Configuration | File | Line | Default | Range |
|--------------|------|------|---------|-------|
| Context Window | chat.py | ~48 | 20 | 5-100 |
| Temperature | ollama_client.py | ~20 | 0.7 | 0.0-2.0 |
| Max Tokens | ollama_client.py | ~21 | 2000 | 100-8000 |
| Model | .env | - | gemma2:2b | Any Ollama model |
| Timeout | .env | - | 120s | 30-300s |


***




