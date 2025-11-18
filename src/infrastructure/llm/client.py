"""OpenAI LLM client."""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import json

from config.settings import get_settings


class LLMClient:
    """LLM client - KISS: Simple interface."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text using LLM."""
        response = await self.client.chat.completions.create(
            model=model or self.settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful database query assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature or self.settings.openai_temperature,
            max_tokens=max_tokens or self.settings.openai_max_tokens
        )
        
        return response.choices[0].message.content
    
    async def generate_with_function_calling(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate with function calling for structured output."""
        response = await self.client.chat.completions.create(
            model=model or self.settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful database query assistant."},
                {"role": "user", "content": prompt}
            ],
            functions=functions,
            function_call="auto"
        )
        
        message = response.choices[0].message
        
        if message.function_call:
            return {
                "function_name": message.function_call.name,
                "arguments": json.loads(message.function_call.arguments)
            }
        
        return {"content": message.content}

