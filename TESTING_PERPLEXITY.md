# Testing Perplexity API Integration

This guide shows you how to test if Perplexity API is working correctly with The Discoverer.

## Quick Test

### 1. Set up your .env file

Make sure you have a `.env` file with Perplexity configuration:

```bash
# Copy example if you don't have .env
cp .env.example .env

# Edit .env and set:
LLM_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_actual_perplexity_api_key_here
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
PERPLEXITY_MODEL_COMPLEX=llama-3.1-sonar-large-128k-online
```

### 2. Run the test script

```bash
python3 test_perplexity.py
```

This will:
- Check your configuration
- Initialize the LLM client
- Test a simple query generation
- Show any errors if something is wrong

### 3. Test through the API

Start the server:
```bash
make run
```

Then test with curl:
```bash
# Test a simple query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me all users",
    "database_ids": []
  }'
```

Or use the interactive API docs:
```bash
# Open in browser
http://localhost:8000/docs
```

## Manual Testing Steps

### Step 1: Verify Configuration

```python
from config.settings import get_settings

settings = get_settings()
print(f"Provider: {settings.llm_provider}")
print(f"Perplexity API Key: {'Set' if settings.perplexity_api_key else 'Not set'}")
print(f"Model: {settings.perplexity_model}")
```

### Step 2: Test LLM Client Directly

```python
import asyncio
from src.infrastructure.llm.client import LLMClient

async def test():
    client = LLMClient()
    print(f"Base URL: {client.client.base_url}")
    print(f"Default Model: {client.default_model}")
    
    response = await client.generate("Generate a SQL query to select all users")
    print(f"Response: {response}")

asyncio.run(test())
```

### Step 3: Test Query Generation

```python
import asyncio
from src.infrastructure.llm.client import LLMClient
from src.infrastructure.llm.generators.sql_generator import SQLGenerator

async def test():
    client = LLMClient()
    generator = SQLGenerator(client)
    
    schema_context = [{
        "payload": {
            "database_id": "test_db",
            "table": "users",
            "columns": ["id", "name", "email"]
        }
    }]
    
    query = await generator.generate("show me all users", schema_context)
    print(f"Generated Query: {query.generated_query}")

asyncio.run(test())
```

## Expected Results

### ✅ Success Indicators

- Test script shows "✓ Perplexity integration test PASSED!"
- LLM client initializes without errors
- Base URL is `https://api.perplexity.ai`
- Model name starts with `llama-3.1-sonar`
- Query generation returns valid SQL/query strings

### ❌ Common Errors

1. **401 Unauthorized**
   - Your API key is invalid or expired
   - Check your Perplexity API key in `.env`

2. **429 Rate Limit**
   - You've exceeded your API rate limit
   - Wait a bit and try again

3. **Connection Error**
   - Network issue or Perplexity API is down
   - Check your internet connection

4. **Module not found**
   - Missing dependencies
   - Run: `pip install -r requirements.txt`

## Testing Different Models

You can test different Perplexity models by changing in `.env`:

```bash
# Fast model
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online

# Balanced (default)
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online

# Most capable
PERPLEXITY_MODEL=llama-3.1-sonar-huge-128k-online

# Without web search
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-chat
```

Then restart the server and test again.

## Comparing OpenAI vs Perplexity

Run the test script with comparison:
```bash
python3 test_perplexity.py --compare
```

This will test both providers and show you the differences.

## Troubleshooting

### Issue: Settings not updating

Clear the settings cache:
```python
from config.settings import get_settings
get_settings.cache_clear()
```

### Issue: Wrong provider being used

Check your `.env` file:
```bash
grep LLM_PROVIDER .env
```

Make sure it says `LLM_PROVIDER=perplexity` (not `openai`)

### Issue: API key not working

1. Verify your API key at https://www.perplexity.ai/settings/api
2. Make sure there are no extra spaces in `.env` file
3. Restart the server after changing `.env`

## Next Steps

Once testing passes:
1. Test with actual database queries
2. Monitor API usage and costs
3. Compare performance between OpenAI and Perplexity
4. Adjust models based on your needs

