"""Prometheus metrics API route."""
from fastapi import APIRouter
from fastapi.responses import Response
from src.utils.prometheus_metrics import MetricsCollector


router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/prometheus")
async def prometheus_metrics():
    """Get Prometheus metrics."""
    metrics = MetricsCollector.get_metrics()
    return Response(content=metrics, media_type="text/plain; version=0.0.4")


