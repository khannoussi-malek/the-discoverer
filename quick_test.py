#!/usr/bin/env python3
"""Quick test to verify Perplexity is configured correctly."""
import os
import asyncio

# Force Perplexity
os.environ['LLM_PROVIDER'] = 'perplexity'

from config.settings import get_settings
from src.infrastructure.llm.client import LLMClient

async def quick_test():
    get_settings.cache_clear()
    settings = get_settings()
    
    print("Configuration:")
    print(f"  Provider: {settings.llm_provider}")
    print(f"  API Key: {'✓ Set' if settings.perplexity_api_key and settings.perplexity_api_key != 'your_perplexity_api_key_here' else '✗ Not set'}")
    print(f"  Model: {settings.perplexity_model}")
    print(f"  Base URL: {settings.perplexity_base_url}")
    print()
    
    if not settings.perplexity_api_key or settings.perplexity_api_key == 'your_perplexity_api_key_here':
        print("⚠️  Please set PERPLEXITY_API_KEY in your .env file")
        return
    
    try:
        client = LLMClient()
        print(f"Client initialized:")
        print(f"  Base URL: {client.client.base_url}")
        print(f"  Model: {client.default_model}")
        print()
        
        print("Testing simple generation...")
        response = await client.generate("Say hello in one word")
        print(f"✓ Success! Response: {response}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
