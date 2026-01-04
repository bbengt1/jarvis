# LLM Provider System

> Multi-provider architecture for flexible AI backend

## Overview

J.A.R.V.I.S. supports multiple LLM providers through a unified interface. You can switch providers at runtime without changing application code.

## Supported Providers

| Provider | Type | Pricing | Best For |
|----------|------|---------|----------|
| **Ollama** | Local | Free | Privacy, offline use, development |
| **OpenAI** | Cloud | Per-token | GPT-4 quality, large context |
| **Anthropic** | Cloud | Per-token | Claude's reasoning, safety |
| **Google** | Cloud | Per-token | Gemini speed, multimodal |
| **xAI** | Cloud | Per-token | Grok's style, real-time info |

## Configuration

### Environment Variables

```bash
# .env file

# Select provider (ollama, openai, anthropic, google, xai)
LLM__PROVIDER=ollama
LLM__MODEL=llama3.2

# Provider-specific settings
LLM__OLLAMA_BASE_URL=http://localhost:11434

# API Keys (only needed for cloud providers)
LLM__OPENAI_API_KEY=sk-...
LLM__ANTHROPIC_API_KEY=sk-ant-...
LLM__GOOGLE_API_KEY=AIza...
LLM__XAI_API_KEY=xai-...

# Generation parameters
LLM__TEMPERATURE=0.7
LLM__MAX_TOKENS=1024
```

### Web UI Configuration

Access `http://localhost:8080` to configure:

1. Select provider from dropdown
2. Choose model for that provider
3. Enter API key if required
4. Test connection
5. Adjust temperature and max tokens

## Provider Details

### Ollama (Local)

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start server
ollama serve

# Pull model
ollama pull llama3.2
```

**Models:**
- `llama3.2` - Meta's latest, great general purpose
- `llama3.1` - Previous generation, larger context
- `mistral` - Fast, good coding
- `codellama` - Code-focused
- `phi3` - Microsoft's small model

**Pros:** Free, private, no internet required
**Cons:** Requires local GPU/CPU resources

---

### OpenAI

**Setup:**
1. Get API key from https://platform.openai.com
2. Set `LLM__OPENAI_API_KEY`

**Models:**
- `gpt-4o` - Most capable, multimodal
- `gpt-4o-mini` - Faster, cheaper
- `gpt-4-turbo` - Previous flagship
- `gpt-3.5-turbo` - Fast, budget option

**Pros:** Industry standard, large context windows
**Cons:** API costs, data sent to cloud

---

### Anthropic (Claude)

**Setup:**
1. Get API key from https://console.anthropic.com
2. Set `LLM__ANTHROPIC_API_KEY`

**Models:**
- `claude-sonnet-4-20250514` - Balanced capability/speed
- `claude-3-5-haiku-20241022` - Fast, efficient
- `claude-3-opus-20240229` - Most capable

**Pros:** Strong reasoning, safety focused
**Cons:** API costs

---

### Google (Gemini)

**Setup:**
1. Get API key from https://aistudio.google.com
2. Set `LLM__GOOGLE_API_KEY`

**Models:**
- `gemini-1.5-flash` - Fast, efficient
- `gemini-1.5-pro` - More capable
- `gemini-2.0-flash` - Latest generation

**Pros:** Fast, multimodal, generous free tier
**Cons:** Newer ecosystem

---

### xAI (Grok)

**Setup:**
1. Get API key from https://x.ai
2. Set `LLM__XAI_API_KEY`

**Models:**
- `grok-2-latest` - Current flagship
- `grok-beta` - Experimental features

**Pros:** Unique personality, real-time info
**Cons:** Newer provider

## Usage Patterns

### Basic Generation

```python
from brain.llm import LLMClient
from core.config import LLMSettings

client = LLMClient(LLMSettings())

messages = [
    {"role": "user", "content": "What's the weather like?"}
]

response = await client.generate(messages)
print(response)
```

### With System Prompt

```python
response = await client.generate(
    messages,
    system="You are a pirate. Respond accordingly."
)
```

### Streaming

```python
async for chunk in client.generate_stream(messages):
    print(chunk, end="", flush=True)
print()  # Newline at end
```

### Runtime Provider Switching

```python
from core.config import LLMProvider

# Start with Ollama for privacy
await client.switch_provider(LLMProvider.OLLAMA, "llama3.2")

# Switch to Claude for complex reasoning
await client.switch_provider(LLMProvider.ANTHROPIC, "claude-sonnet-4-20250514")

# Switch to GPT-4 for coding
await client.switch_provider(LLMProvider.OPENAI, "gpt-4o")
```

## Creating a Custom Provider

```python
# brain/providers/custom.py
from collections.abc import AsyncIterator
from typing import Any

from brain.providers.base import LLMProviderBase


class CustomProvider(LLMProviderBase):
    """Custom LLM provider."""

    async def generate(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        # Implement API call
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        response = await self._call_api(full_messages)
        return response["content"]

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> AsyncIterator[str]:
        # Implement streaming
        async for chunk in self._stream_api(messages):
            yield chunk["content"]

    async def close(self) -> None:
        # Cleanup connections
        pass
```

Then register in `brain/llm.py`:

```python
from brain.providers.custom import CustomProvider

# In LLMClient._get_provider():
case LLMProvider.CUSTOM:
    provider_class = CustomProvider
```

## Best Practices

### 1. Start Local, Scale Cloud

Use Ollama for development, switch to cloud for production:

```python
if os.getenv("ENVIRONMENT") == "development":
    settings.provider = LLMProvider.OLLAMA
else:
    settings.provider = LLMProvider.ANTHROPIC
```

### 2. Handle Rate Limits

Cloud providers have rate limits. Implement backoff:

```python
import asyncio

async def generate_with_retry(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.generate(messages)
        except RateLimitError:
            await asyncio.sleep(2 ** attempt)
    raise Exception("Max retries exceeded")
```

### 3. Cost Awareness

Track token usage for cloud providers:

```python
# Most providers return usage info
response = await provider.generate_with_usage(messages)
print(f"Used {response.usage.total_tokens} tokens")
```

### 4. Model Selection

| Task | Recommended |
|------|-------------|
| General chat | llama3.2, gpt-4o-mini, gemini-1.5-flash |
| Complex reasoning | claude-sonnet-4, gpt-4o |
| Coding | codellama, gpt-4o |
| Fast responses | gemini-1.5-flash, gpt-3.5-turbo |
| Privacy critical | Ollama (local) |
