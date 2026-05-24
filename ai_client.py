"""
ai_client.py - Universal AI Client with Fallback Logic
Supports NVIDIA (Primary), OpenAI (Fallback), and Ollama (Local)
"""
import json
import os
from openai import OpenAI

# Configuration - Replace with environment variables in production
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# Clients
_NVIDIA_CLIENT = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
_OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
_OLLAMA_CLIENT = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama") # Ollama usually doesn't need a key

# Models
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
OPENAI_MODEL = "gpt-4o-mini"
OLLAMA_MODEL = "llama3.1"

def _try_call(client, model, system, user, max_tokens):
    """Internal helper to make a chat completion call."""
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        raw = resp.choices[0].message.content.strip()
        
        # Clean up JSON if LLM returns it in markdown blocks
        if raw.startswith("```"):
            parts = raw.split("```")
            if len(parts) > 1:
                raw = parts[1]
                if raw.startswith("json"):
                    raw = raw[4:]
        
        return json.loads(raw.strip())
    except Exception as e:
        print(f"      [AI Client] {model} failed: {e}")
        return None

def call_ai(system: str, user: str, max_tokens: int = 1200) -> dict:
    """
    Primary entry point for AI calls with fallback logic.
    NVIDIA -> OpenAI -> Ollama
    """
    # 1. Try NVIDIA
    result = _try_call(_NVIDIA_CLIENT, NVIDIA_MODEL, system, user, max_tokens)
    if result and "error" not in result:
        return result

    # 2. Try OpenAI Fallback
    if _OPENAI_CLIENT:
        print("      [AI Client] Falling back to OpenAI...")
        result = _try_call(_OPENAI_CLIENT, OPENAI_MODEL, system, user, max_tokens)
        if result and "error" not in result:
            return result

    # 3. Try Ollama Fallback (Local)
    print("      [AI Client] Falling back to local Ollama...")
    result = _try_call(_OLLAMA_CLIENT, OLLAMA_MODEL, system, user, max_tokens)
    if result and "error" not in result:
        return result

    return {"error": "All AI backends failed", "raw": ""}
