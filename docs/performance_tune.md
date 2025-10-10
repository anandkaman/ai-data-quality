## Solutions for low RAM System 

### Solution 1: Optimize Ollama Memory (RECOMMENDED)

Tell Ollama to use **less RAM** by keeping model **partially in memory**:

**Create/Edit Ollama config:**

**Windows:**
```bash
# Set environment variable
setx OLLAMA_NUM_PARALLEL 1
setx OLLAMA_MAX_LOADED_MODELS 1
setx OLLAMA_MAX_QUEUE 1
```

**Or create:** `C:\Users\YourUsername\.ollama\config.json`

```json
{
  "num_parallel": 1,
  "max_loaded_models": 1,
  "max_queue": 1,
  "num_gpu": 0,
  "num_thread": 4,
  "context_length": 2048
}
```

**Then restart Ollama:**
```bash
# Close Ollama from system tray
# Start Ollama again
```

***

### Solution 2: Use Smaller Context Window

Your app is sending **20 previous messages** + current message. On low RAM, reduce this:

**backend/app/api/v1/routes/chat.py** - Line ~48:

```python
# BEFORE (uses ~500MB RAM)
previous_messages = db.query(ChatMessage).filter(
    ChatMessage.chat_session_id == chat_session.id
).order_by(ChatMessage.created_at.asc()).limit(20).all()

# AFTER (uses ~100MB RAM)
previous_messages = db.query(ChatMessage).filter(
    ChatMessage.chat_session_id == chat_session.id
).order_by(ChatMessage.created_at.asc()).limit(5).all()  # Only 5 messages
```

***

### Solution 3: Reduce Model Parameters

**backend/app/services/llm_engine/ollama_client.py:**

```python
async def generate(
    self,
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 500,  # ← REDUCE from 2000 to 500
    top_p: float = 0.9,
    top_k: int = 40,
    repeat_penalty: float = 1.1,
    stream: bool = False
):
```

**Why this helps:**
- Lower `max_tokens` = Less memory needed
- Faster generation = Less time in memory

***

### Solution 4: Enable Model Unloading

Add this to your **ollama_client.py**:

```python
class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = httpx.Timeout(settings.OLLAMA_TIMEOUT, connect=10.0)
    
    async def unload_model(self):
        """Unload model from memory after use"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "keep_alive": 0  # Unload immediately
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to unload model: {e}")
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs):
        # ... existing code ...
        
        # After generation, unload model to free RAM
        # await self.unload_model()  # Uncomment if needed
        
        return response
```

**Then in chat.py:**

```python
# After getting AI response
ai_response = await ollama_client.generate(...)

# Unload model to free memory (optional)
await ollama_client.unload_model()
```

**Trade-off:** Next request will be slower (needs to reload model)

***


## Monitoring Commands

### Check RAM usage:
```bash
# PowerShell
Get-Process | Sort-Object WS -Descending | Select-Object -First 10 Name, @{Name="Memory(MB)";Expression={$_.WS / 1MB}}
```

### Check Ollama memory:
```bash
# Task Manager → Details → Find "ollama.exe"
# Check "Memory (Private Working Set)"
```

***

## Long-term Solutions

If you frequently use AI models, consider:

1. **Add 8GB RAM** → 16GB total (best solution) - ~$30-50
2. **Use cloud GPU** → Google Colab, RunPod
3. **Use API instead** → OpenAI API (paid but no local resources)

***


