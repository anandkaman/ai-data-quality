# Model Configuration Guide

## Overview

This guide explains how to configure and optimize LLM models (Ollama) for the AI Data Quality Guardian system.

---

## Model Architecture

```
User Request → FastAPI → Ollama Client → Ollama Server → LLM Model
                  ↓
            Configuration
              (.env + code)
```

---

## Configuration Files

### 1. Environment Variables (.env)

**File:** `backend/.env`

```
# ======================
# OLLAMA/LLM Configuration
# ======================
OLLAMA_BASE_URL=http://localhost:11434    # Ollama server URL
OLLAMA_MODEL=gemma2:2b                     # Default model
OLLAMA_TIMEOUT=120                         # Request timeout (seconds)
```

#### OLLAMA_BASE_URL

**Default:** `http://localhost:11434`

**Options:**

```
# Local Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Remote Ollama server
OLLAMA_BASE_URL=http://192.168.1.100:11434

# Docker container
OLLAMA_BASE_URL=http://ollama-container:11434

# Custom port
OLLAMA_BASE_URL=http://localhost:8080
```

---

#### OLLAMA_MODEL

**Default:** `gemma2:2b`

**Available Models:**

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `phi3` | 2.3GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast responses |
| `gemma2:2b` | 1.6GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **Recommended** |
| `llama3.2` | 4.7GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | High quality |
| `mistral` | 7.2GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Advanced tasks |
| `qwen2.5` | 7.6GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Multilingual |
| `codellama` | 7.0GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Code generation |
| `llama3.2:70b` | 40GB | ⚡ | ⭐⭐⭐⭐⭐⭐ | Maximum quality |

**Change model:**
```
OLLAMA_MODEL=mistral
```

**Download new model:**
```
ollama pull mistral
ollama pull llama3.2
ollama pull codellama
```

---

#### OLLAMA_TIMEOUT

**Default:** `120` seconds (2 minutes)

**Recommendations:**

| Model Size | Timeout | Reason |
|------------|---------|--------|
| < 3GB | 60s | Fast response |
| 3-8GB | 120s | **Recommended** |
| 8-15GB | 180s | Slower models |
| 15GB+ | 300s | Very large models |

```
# Fast models
OLLAMA_TIMEOUT=60

# Large models
OLLAMA_TIMEOUT=300

# Testing (quick fail)
OLLAMA_TIMEOUT=30
```

---

### 2. Ollama Client Configuration

**File:** `backend/app/services/llm_engine/ollama_client.py`

```
class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = httpx.Timeout(
            settings.OLLAMA_TIMEOUT,  # ← Change timeout here
            connect=10.0,              # Connection timeout
            read=settings.OLLAMA_TIMEOUT,
            write=10.0
        )
```

#### Connection Timeout

Controls how long to wait for connection:

```
connect=10.0  # 10 seconds to connect
```

**Recommendations:**
- Local: `5.0` seconds
- LAN: `10.0` seconds
- Internet: `30.0` seconds

#### Read Timeout

How long to wait for model response:

```
read=settings.OLLAMA_TIMEOUT  # Uses .env value
```

---

### 3. Generation Parameters

**File:** `backend/app/services/llm_engine/ollama_client.py`

```
async def generate(
    self,
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,     # Creativity
    max_tokens: int = 2000,       # Response length
    top_p: float = 0.9,           # Nucleus sampling
    top_k: int = 40,              # Token selection
    repeat_penalty: float = 1.1,  # Prevent repetition
    stream: bool = False          # Streaming response
):
```

---

#### Temperature

Controls randomness/creativity.

**Range:** 0.0 - 2.0

| Value | Behavior | Use Case |
|-------|----------|----------|
| 0.0 - 0.3 | Deterministic, focused | Code, technical docs |
| 0.4 - 0.6 | Slightly varied | Data analysis |
| 0.7 - 0.8 | Balanced | **General chat** |
| 0.9 - 1.2 | Creative | Brainstorming |
| 1.3+ | Very random | Creative writing |

```
# Technical documentation
temperature=0.2

# Creative responses
temperature=1.0
```

---

#### Max Tokens

Controls response length.

**Range:** 50 - 8000+

| Tokens | ~Words | Response Type |
|--------|--------|---------------|
| 100 | 75 | Very short |
| 500 | 375 | Short answer |
| 1000 | 750 | Medium explanation |
| 2000 | 1500 | **Detailed response** |
| 4000 | 3000 | Long article |
| 8000+ | 6000+ | Full documents |

**Memory Impact:**
- Higher tokens = More memory
- Higher tokens = Slower response

```
# Quick answers
max_tokens=500

# Detailed explanations
max_tokens=3000
```

---

#### Top P (Nucleus Sampling)

Controls diversity by probability threshold.

**Range:** 0.0 - 1.0

| Value | Behavior |
|-------|----------|
| 0.5 | Very focused |
| 0.7 | Moderately focused |
| 0.9 | **Balanced** (default) |
| 0.95 | More diverse |
| 1.0 | Maximum diversity |

```
# Focused responses
top_p=0.7

# Diverse responses
top_p=0.95
```

---

#### Top K

Limits token selection pool.

**Range:** 1 - 100

| Value | Behavior |
|-------|----------|
| 10 | Very limited |
| 20 | Focused |
| 40 | **Balanced** (default) |
| 60 | More options |
| 100 | Maximum variety |

```
# Focused answers
top_k=20

# Varied responses
top_k=60
```

---

#### Repeat Penalty

Prevents repetitive text.

**Range:** 1.0 - 2.0

| Value | Effect |
|-------|--------|
| 1.0 | No penalty |
| 1.1 | **Light penalty** (default) |
| 1.3 | Moderate penalty |
| 1.5 | Strong penalty |
| 2.0 | Maximum penalty |

```
# Allow some repetition
repeat_penalty=1.0

# Prevent repetition
repeat_penalty=1.5
```

---

## Model Switching

### Via Frontend Model Switcher

1. Click model dropdown in chat interface
2. Select model from list
3. Or pull new model with terminal output

### Via .env File

```
# Change this and restart backend
OLLAMA_MODEL=llama3.2
```

```
# Restart backend
cd backend
uvicorn app.main:app --reload
```

### Via API

```
# Switch model
curl -X POST http://localhost:8000/api/v1/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_name": "mistral"}'

# Pull new model
curl -X POST http://localhost:8000/api/v1/models/pull/llama3.2
```

---

## Performance Optimization

### For Speed ⚡

```
# Use small model
OLLAMA_MODEL=phi3

# Reduce tokens
max_tokens=500

# Lower temperature
temperature=0.3

# Reduce timeout
OLLAMA_TIMEOUT=60
```

### For Quality ⭐

```
# Use large model
OLLAMA_MODEL=mistral

# Increase tokens
max_tokens=3000

# Balanced temperature
temperature=0.7

# Increase timeout
OLLAMA_TIMEOUT=180
```

### For Determinism 🎯

```
# Low temperature
temperature=0.2

# Low top_p
top_p=0.7

# Low top_k
top_k=20

# No randomness
# (same question = same answer)
```

### For Creativity 🎨

```
# High temperature
temperature=1.0

# High top_p
top_p=0.95

# High top_k
top_k=60

# More randomness
# (varied responses)
```

---

## Hardware Requirements

### Minimum (2-3GB models)

- **RAM:** 8GB
- **GPU:** Optional (CPU works)
- **Storage:** 10GB free

**Models:** phi3, gemma2:2b

### Recommended (7-8GB models)

- **RAM:** 16GB
- **GPU:** 6GB VRAM (NVIDIA/AMD)
- **Storage:** 20GB free

**Models:** mistral, llama3.2, qwen2.5

### High-End (15GB+ models)

- **RAM:** 32GB+
- **GPU:** 16GB+ VRAM
- **Storage:** 50GB+ free

**Models:** llama3.2:70b, mixtral

---

## Troubleshooting

### Issue: Timeout errors

```
# Increase timeout
OLLAMA_TIMEOUT=300
```

### Issue: Connection refused

```
# Check Ollama is running
ollama list

# Restart Ollama
# Windows: 
Restart Ollama app
# Linux/Mac:
sudo systemctl restart ollama
```

### Issue: Model not found

```
# Pull the model
ollama pull gemma2:2b

# Check available models
ollama list
```

### Issue: Slow responses

```
# Use smaller model
OLLAMA_MODEL=phi3

# Reduce max_tokens
max_tokens=1000
```

### Issue: Out of memory

```
# Use smaller model
OLLAMA_MODEL=phi3

# Or restart Ollama to free memory
ollama stop
ollama serve
```

### Issue: Repetitive responses

```
# Increase repeat_penalty
repeat_penalty=1.5

# Increase top_k
top_k=60
```

---

## Model Comparison Chart

| Feature | phi3 | gemma2:2b | llama3.2 | mistral |
|---------|------|-----------|----------|---------|
| Size | 2.3GB | 1.6GB | 4.7GB | 7.2GB |
| Speed | ⚡⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ |
| Quality | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Code | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Data Science | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Multilingual | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Quick Reference

```
# Fast & Light
OLLAMA_MODEL=phi3
temperature=0.3
max_tokens=500
OLLAMA_TIMEOUT=60

# Balanced (Recommended)
OLLAMA_MODEL=gemma2:2b
temperature=0.7
max_tokens=2000
OLLAMA_TIMEOUT=120

# High Quality
OLLAMA_MODEL=mistral
temperature=0.7
max_tokens=3000
OLLAMA_TIMEOUT=180

# Creative
OLLAMA_MODEL=gemma2:2b
temperature=1.0
max_tokens=2000
top_p=0.95
OLLAMA_TIMEOUT=120
```

---

## Testing Different Configurations

```
# Test current configuration
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What is data quality?",
    "system_prompt": "Be brief"
  }'
```

**Monitor response time and quality, then adjust settings accordingly.**


