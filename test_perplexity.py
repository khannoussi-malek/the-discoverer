#!/usr/bin/env python3
"""Test script for Perplexity API integration."""
import os
import sys
import asyncio
from config.settings import get_settings
from src.infrastructure.llm.client import LLMClient


async def test_perplexity():
    """Test Perplexity API integration."""
    print("=" * 60)
    print("Testing Perplexity API Integration")
    print("=" * 60)
    
    # Force Perplexity for testing
    original_provider = os.environ.get('LLM_PROVIDER')
    os.environ['LLM_PROVIDER'] = 'perplexity'
    
    # Clear settings cache to reload
    get_settings.cache_clear()
    settings = get_settings()
    
    print(f"\n1. Configuration Check:")
    print(f"   LLM Provider: {settings.llm_provider}")
    print(f"   Perplexity API Key: {'✓ Set' if settings.perplexity_api_key else '✗ Not set'}")
    print(f"   Perplexity Model: {settings.perplexity_model}")
    print(f"   Perplexity Base URL: {settings.perplexity_base_url}")
    
    if not settings.perplexity_api_key:
        print("\n⚠️  ERROR: PERPLEXITY_API_KEY is not set in .env file!")
        print("   Please set PERPLEXITY_API_KEY in your .env file")
        return False
    
    if settings.llm_provider.lower() != "perplexity":
        print(f"\n⚠️  WARNING: LLM_PROVIDER is set to '{settings.llm_provider}'")
        print("   Set LLM_PROVIDER=perplexity in your .env file to use Perplexity")
        print("   Testing with Perplexity anyway...")
    
    print(f"\n2. Initializing LLM Client...")
    try:
        client = LLMClient()
        print(f"   ✓ Client initialized")
        print(f"   Base URL: {client.client.base_url}")
        print(f"   Default Model: {client.default_model}")
        print(f"   Complex Model: {client.complex_model}")
    except Exception as e:
        print(f"   ✗ Error initializing client: {e}")
        return False
    
    print(f"\n3. Testing Simple Query Generation...")
    
    # Try different model names if the default fails
    models_to_try = [
        settings.perplexity_model,  # Try configured model first
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-sonar-small-128k-online",
        "sonar",
        "sonar-pro",
        "pplx-7b-online",
        "pplx-70b-online"
    ]
    
    test_prompt = "Generate a SQL query to select all users from a users table"
    print(f"   Prompt: {test_prompt}")
    
    try:
        for model_name in models_to_try:
            try:
                print(f"   Trying model: {model_name}...")
                response = await client.generate(test_prompt, model=model_name)
                print(f"   ✓ Response received with model '{model_name}'!")
                print(f"   Response: {response[:200]}..." if len(response) > 200 else f"   Response: {response}")
                print(f"\n   💡 Tip: Update PERPLEXITY_MODEL={model_name} in your .env file")
                return True
            except Exception as e:
                error_str = str(e)
                if "Invalid model" in error_str:
                    print(f"   ✗ Model '{model_name}' is invalid, trying next...")
                    continue
                else:
                    print(f"   ✗ Error with model '{model_name}': {e}")
                    print(f"   Error type: {type(e).__name__}")
                    if "401" in error_str or "Unauthorized" in error_str:
                        print(f"   → This usually means the API key is invalid")
                    elif "429" in error_str:
                        print(f"   → This usually means rate limit exceeded")
                    elif "Connection" in error_str:
                        print(f"   → This usually means network/connection issue")
                    return False
        
        print(f"\n   ✗ All model names failed!")
        print(f"   → Check Perplexity docs for correct model names:")
        print(f"   → https://docs.perplexity.ai/getting-started/models")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ['LLM_PROVIDER'] = original_provider
        elif 'LLM_PROVIDER' in os.environ:
            del os.environ['LLM_PROVIDER']


async def test_openai():
    """Test OpenAI API integration for comparison."""
    print("\n" + "=" * 60)
    print("Testing OpenAI API Integration (for comparison)")
    print("=" * 60)
    
    # Temporarily switch to OpenAI
    original_provider = os.environ.get('LLM_PROVIDER', 'openai')
    os.environ['LLM_PROVIDER'] = 'openai'
    
    get_settings.cache_clear()
    settings = get_settings()
    
    print(f"\n1. Configuration Check:")
    print(f"   LLM Provider: {settings.llm_provider}")
    print(f"   OpenAI API Key: {'✓ Set' if settings.openai_api_key else '✗ Not set'}")
    
    if not settings.openai_api_key:
        print("\n⚠️  OpenAI API key not set, skipping OpenAI test")
        os.environ['LLM_PROVIDER'] = original_provider
        return
    
    try:
        client = LLMClient()
        print(f"   ✓ Client initialized")
        print(f"   Default Model: {client.default_model}")
        
        test_prompt = "Generate a SQL query to select all users from a users table"
        print(f"\n2. Testing with prompt: {test_prompt}")
        response = await client.generate(test_prompt)
        print(f"   ✓ OpenAI response received!")
        print(f"   Response: {response[:200]}..." if len(response) > 200 else f"   Response: {response}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    finally:
        os.environ['LLM_PROVIDER'] = original_provider


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider Test Suite")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found!")
        print("   Creating .env from .env.example...")
        if os.path.exists('.env.example'):
            os.system('cp .env.example .env')
            print("   ✓ .env file created. Please edit it with your API keys.")
        else:
            print("   ✗ .env.example not found either!")
            sys.exit(1)
    
    # Run tests
    result = asyncio.run(test_perplexity())
    
    # Optionally test OpenAI
    if '--compare' in sys.argv:
        asyncio.run(test_openai())
    
    print("\n" + "=" * 60)
    if result:
        print("✓ Perplexity integration test PASSED!")
    else:
        print("✗ Perplexity integration test FAILED!")
        print("\nTroubleshooting:")
        print("1. Make sure PERPLEXITY_API_KEY is set in .env file")
        print("2. Make sure LLM_PROVIDER=perplexity in .env file")
        print("3. Check that your API key is valid")
        print("4. Check your internet connection")
    print("=" * 60 + "\n")

