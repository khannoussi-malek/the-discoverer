"""LLM API cost tracking utilities."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class LLMUsage:
    """LLM API usage record."""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    operation: str  # "query_generation", "embedding", etc.
    user_id: Optional[str] = None
    query_id: Optional[str] = None


class CostTracker:
    """Track LLM API usage and costs."""
    
    # Pricing per 1K tokens (as of 2024, adjust as needed)
    PRICING = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        "text-embedding-3-small": {"prompt": 0.00002, "completion": 0.0},
        "text-embedding-3-large": {"prompt": 0.00013, "completion": 0.0},
        "text-embedding-ada-002": {"prompt": 0.0001, "completion": 0.0},
    }
    
    def __init__(self):
        self._usage: List[LLMUsage] = []
    
    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        operation: str = "query_generation",
        user_id: Optional[str] = None,
        query_id: Optional[str] = None
    ) -> LLMUsage:
        """Record LLM API usage."""
        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        
        usage = LLMUsage(
            timestamp=datetime.utcnow(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            operation=operation,
            user_id=user_id,
            query_id=query_id
        )
        
        self._usage.append(usage)
        return usage
    
    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost in USD."""
        # Get base model name (handle variants)
        base_model = model.split("-")[0] + "-" + model.split("-")[1] if "-" in model else model
        
        pricing = self.PRICING.get(model) or self.PRICING.get(base_model)
        if not pricing:
            # Default pricing if model not found
            pricing = {"prompt": 0.001, "completion": 0.002}
        
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        return prompt_cost + completion_cost
    
    def get_total_cost(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model: Optional[str] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> float:
        """Get total cost for a period."""
        filtered = self._filter_usage(
            start_date=start_date,
            end_date=end_date,
            model=model,
            operation=operation,
            user_id=user_id
        )
        
        return sum(u.cost_usd for u in filtered)
    
    def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model: Optional[str] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage statistics."""
        filtered = self._filter_usage(
            start_date=start_date,
            end_date=end_date,
            model=model,
            operation=operation,
            user_id=user_id
        )
        
        if not filtered:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "average_tokens_per_request": 0,
                "average_cost_per_request": 0.0
            }
        
        total_tokens = sum(u.total_tokens for u in filtered)
        total_cost = sum(u.cost_usd for u in filtered)
        
        return {
            "total_requests": len(filtered),
            "total_tokens": total_tokens,
            "total_prompt_tokens": sum(u.prompt_tokens for u in filtered),
            "total_completion_tokens": sum(u.completion_tokens for u in filtered),
            "total_cost_usd": total_cost,
            "average_tokens_per_request": total_tokens / len(filtered),
            "average_cost_per_request": total_cost / len(filtered),
            "start_date": min(u.timestamp for u in filtered).isoformat(),
            "end_date": max(u.timestamp for u in filtered).isoformat()
        }
    
    def get_cost_by_model(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by model."""
        filtered = self._filter_usage(start_date=start_date, end_date=end_date)
        
        costs_by_model = defaultdict(float)
        for usage in filtered:
            costs_by_model[usage.model] += usage.cost_usd
        
        return dict(costs_by_model)
    
    def get_cost_by_operation(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by operation."""
        filtered = self._filter_usage(start_date=start_date, end_date=end_date)
        
        costs_by_operation = defaultdict(float)
        for usage in filtered:
            costs_by_operation[usage.operation] += usage.cost_usd
        
        return dict(costs_by_operation)
    
    def get_daily_costs(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get daily cost breakdown."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        daily_costs = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "requests": 0})
        
        for usage in self._usage:
            if start_date <= usage.timestamp <= end_date:
                date_key = usage.timestamp.date().isoformat()
                daily_costs[date_key]["cost"] += usage.cost_usd
                daily_costs[date_key]["tokens"] += usage.total_tokens
                daily_costs[date_key]["requests"] += 1
        
        return [
            {
                "date": date,
                "cost_usd": stats["cost"],
                "total_tokens": stats["tokens"],
                "requests": stats["requests"]
            }
            for date, stats in sorted(daily_costs.items())
        ]
    
    def _filter_usage(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model: Optional[str] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[LLMUsage]:
        """Filter usage records."""
        filtered = self._usage
        
        if start_date:
            filtered = [u for u in filtered if u.timestamp >= start_date]
        
        if end_date:
            filtered = [u for u in filtered if u.timestamp <= end_date]
        
        if model:
            filtered = [u for u in filtered if u.model == model]
        
        if operation:
            filtered = [u for u in filtered if u.operation == operation]
        
        if user_id:
            filtered = [u for u in filtered if u.user_id == user_id]
        
        return filtered


