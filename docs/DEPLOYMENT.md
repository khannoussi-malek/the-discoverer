# Deployment Guide

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- OpenAI API key (for LLM features)

## Local Development

1. Clone repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start services:
```bash
docker-compose up -d
```

5. Run application:
```bash
uvicorn src.api.main:app --reload
```

## Production Deployment

### Docker

1. Build image:
```bash
docker build -t the-discoverer .
```

2. Run container:
```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e QDRANT_URL=http://qdrant:6333 \
  -e REDIS_URL=redis://redis:6379 \
  the-discoverer
```

### Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key
- `QDRANT_URL`: Qdrant vector database URL
- `REDIS_URL`: Redis cache URL

Optional:
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEBUG`: Debug mode (default: False)

## Health Checks

- Health endpoint: `GET /health`
- Returns: `{"status": "healthy"}`

## Monitoring

Monitor:
- Request latency
- Database query time
- Vector search time
- Cache hit rates
- LLM generation time

