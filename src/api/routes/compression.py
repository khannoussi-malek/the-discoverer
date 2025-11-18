"""Compression API routes."""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List

from src.utils.compression import CompressionService, CompressionType


router = APIRouter(prefix="/api/compression", tags=["compression"])


@router.post("/compress")
async def compress_data(
    data: Dict[str, Any] = Body(..., description="Data to compress"),
    compression_type: str = Body("gzip", description="Compression type: gzip, zlib, lzma, or brotli"),
    level: int = Body(6, ge=1, le=9, description="Compression level (1-9)")
):
    """Compress data."""
    try:
        comp_type = CompressionType(compression_type.lower())
        result = CompressionService.compress_json(data, comp_type, level)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decompress")
async def decompress_data(
    compressed_dict: Dict[str, Any] = Body(..., description="Compressed data dict")
):
    """Decompress data."""
    try:
        result = CompressionService.decompress_json(compressed_dict)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stats")
async def get_compression_stats(
    data: Dict[str, Any] = Body(..., description="Data to analyze"),
    compression_types: Optional[List[str]] = Body(None, description="Compression types to test")
):
    """Get compression statistics for different algorithms."""
    try:
        comp_types = None
        if compression_types:
            comp_types = [CompressionType(ct.lower()) for ct in compression_types]
        
        stats = CompressionService.get_compression_stats(data, comp_types)
        return {"stats": stats}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



