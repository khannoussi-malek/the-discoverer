# How to Test Perplexity Integration

## Quick Start Testing

### Method 1: Quick Python Test (Recommended)

```bash
python3 quick_test.py
```

This will:
- Check your configuration
- Initialize the Perplexity client
- Test a simple API call

### Method 2: Full Test Suite

```bash
python3 test_perplexity.py
```

This provides detailed testing with error messages.

### Method 3: Test via API

1. **Start the server:**
   ```bash
   make run
   ```

2. **Test with curl:**
   ```bash
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "show me all users",
       "database_ids": []
     }'
   ```

3. **Or use the interactive docs:**
   - Open: http://localhost:8000/docs
   - Try the `/api/query` endpoint

## Setup Steps

### 1. Configure .env file

```bash
# Edit your .env file
nano .env

# Set these values:
LLM_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_actual_api_key_here
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
```

**Important:** Get your API key from: https://www.perplexity.ai/settings/api

### 2. Find the Correct Model Name

Perplexity model names may vary. Check the official docs:
- https://docs.perplexity.ai/getting-started/models

Common model names to try:
- `llama-3.1-sonar-large-128k-online`
- `llama-3.1-sonar-small-128k-online`
- `llama-3.1-sonar-large-128k-chat`
- `sonar`
- `sonar-pro`

If you get a "Invalid model" error, try a different model name from the list above.

### 3. Test Configuration

```python
from config.settings import get_settings

settings = get_settings()
print(f"Provider: {settings.llm_provider}")
print(f"API Key: {'Set' if settings.perplexity_api_key else 'Not set'}")
print(f"Model: {settings.perplexity_model}")
```

## What to Look For

### ✅ Success Indicators

1. **Configuration Check:**
   ```
   Provider: perplexity
   API Key: ✓ Set
   Model: llama-3.1-sonar-large-128k-online
   Base URL: https://api.perplexity.ai
   ```

2. **Client Initialization:**
   ```
   ✓ Client initialized
   Base URL: https://api.perplexity.ai
   ```

3. **API Response:**
   ```
   ✓ Response received!
   Response: SELECT * FROM users...
   ```

### ❌ Common Errors & Solutions

#### Error: "Invalid model"
**Solution:** Update the model name in `.env`:
```bash
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
# Try different models if this doesn't work
```

#### Error: "401 Unauthorized"
**Solution:** 
- Check your API key is correct
- Make sure there are no extra spaces in `.env`
- Verify key at https://www.perplexity.ai/settings/api

#### Error: "429 Rate Limit"
**Solution:** 
- Wait a few minutes
- Check your Perplexity account limits

#### Error: "Connection Error"
**Solution:**
- Check internet connection
- Verify Perplexity API is accessible

## Step-by-Step Testing

### Step 1: Verify Settings

```bash
python3 -c "
from config.settings import get_settings
s = get_settings()
print('Provider:', s.llm_provider)
print('API Key Set:', bool(s.perplexity_api_key))
print('Model:', s.perplexity_model)
"
```

### Step 2: Test Client Initialization

```bash
python3 quick_test.py
```

### Step 3: Test Query Generation

```python
import asyncio
from src.infrastructure.llm.client import LLMClient

async def test():
    client = LLMClient()
    response = await client.generate("Say hello")
    print(response)

asyncio.run(test())
```

### Step 4: Test Full Query Pipeline

Start server and test via API (see Method 3 above).

## Troubleshooting

### Settings Not Updating

```python
from config.settings import get_settings
get_settings.cache_clear()  # Clear cache
settings = get_settings()   # Reload
```

### Wrong Provider Being Used

Check `.env` file:
```bash
grep LLM_PROVIDER .env
```

Should show: `LLM_PROVIDER=perplexity`

### Need to Restart Server

After changing `.env`, always restart:
```bash
# Stop server (Ctrl+C)
# Then restart
make run
```

## Expected Test Output

### Successful Test:
```
Configuration:
  Provider: perplexity
  API Key: ✓ Set
  Model: llama-3.1-sonar-large-128k-online
  Base URL: https://api.perplexity.ai

Client initialized:
  Base URL: https://api.perplexity.ai
  Model: llama-3.1-sonar-large-128k-online

Testing simple generation...
✓ Success! Response: Hello
```

## Next Steps After Testing

Once tests pass:
1. Test with real database queries
2. Monitor API usage
3. Compare performance with OpenAI
4. Adjust models based on needs

