"""Logging middleware."""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import setup_logger

logger = setup_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware - Log all requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response."""
        start_time = time.time()
        
        # Get request ID
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log request
        logger.info(
            f"Request [{request_id}]: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            request_id = getattr(request.state, 'request_id', 'unknown')
            logger.info(
                f"Response [{request_id}]: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            request_id = getattr(request.state, 'request_id', 'unknown')
            logger.error(
                f"Error [{request_id}]: {request.method} {request.url.path} - "
                f"Exception: {str(e)} - "
                f"Time: {process_time:.3f}s"
            )
            raise

