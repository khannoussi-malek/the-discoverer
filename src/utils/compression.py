"""Query result compression utilities."""
import gzip
import json
import zlib
import lzma
from typing import Dict, Any, Optional, Union
from enum import Enum
import base64


class CompressionType(str, Enum):
    """Compression algorithm types."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    LZMA = "lzma"
    BROTLI = "brotli"  # Requires brotli package


class CompressionService:
    """Service for compressing and decompressing query results."""
    
    @staticmethod
    def compress(
        data: Union[str, bytes, Dict[str, Any], list],
        compression_type: CompressionType = CompressionType.GZIP,
        level: int = 6
    ) -> bytes:
        """
        Compress data.
        
        Args:
            data: Data to compress (dict, list, str, or bytes)
            compression_type: Compression algorithm to use
            level: Compression level (1-9, higher = more compression, slower)
        
        Returns:
            Compressed bytes
        """
        # Convert to JSON string if needed
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
            data_bytes = data_str.encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Apply compression
        if compression_type == CompressionType.NONE:
            return data_bytes
        elif compression_type == CompressionType.GZIP:
            return gzip.compress(data_bytes, compresslevel=level)
        elif compression_type == CompressionType.ZLIB:
            return zlib.compress(data_bytes, level=level)
        elif compression_type == CompressionType.LZMA:
            return lzma.compress(data_bytes, preset=level)
        elif compression_type == CompressionType.BROTLI:
            try:
                import brotli
                return brotli.compress(data_bytes, quality=level)
            except ImportError:
                raise ValueError("brotli package not installed. Install with: pip install brotli")
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")
    
    @staticmethod
    def decompress(
        compressed_data: bytes,
        compression_type: CompressionType = CompressionType.GZIP
    ) -> bytes:
        """
        Decompress data.
        
        Args:
            compressed_data: Compressed bytes
            compression_type: Compression algorithm used
        
        Returns:
            Decompressed bytes
        """
        if compression_type == CompressionType.NONE:
            return compressed_data
        elif compression_type == CompressionType.GZIP:
            return gzip.decompress(compressed_data)
        elif compression_type == CompressionType.ZLIB:
            return zlib.decompress(compressed_data)
        elif compression_type == CompressionType.LZMA:
            return lzma.decompress(compressed_data)
        elif compression_type == CompressionType.BROTLI:
            try:
                import brotli
                return brotli.decompress(compressed_data)
            except ImportError:
                raise ValueError("brotli package not installed. Install with: pip install brotli")
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")
    
    @staticmethod
    def compress_to_base64(
        data: Union[str, bytes, Dict[str, Any], list],
        compression_type: CompressionType = CompressionType.GZIP,
        level: int = 6
    ) -> str:
        """
        Compress data and encode as base64 string.
        
        Args:
            data: Data to compress
            compression_type: Compression algorithm to use
            level: Compression level
        
        Returns:
            Base64-encoded compressed string
        """
        compressed = CompressionService.compress(data, compression_type, level)
        return base64.b64encode(compressed).decode('utf-8')
    
    @staticmethod
    def decompress_from_base64(
        base64_data: str,
        compression_type: CompressionType = CompressionType.GZIP
    ) -> bytes:
        """
        Decode base64 and decompress data.
        
        Args:
            base64_data: Base64-encoded compressed string
            compression_type: Compression algorithm used
        
        Returns:
            Decompressed bytes
        """
        compressed = base64.b64decode(base64_data)
        return CompressionService.decompress(compressed, compression_type)
    
    @staticmethod
    def compress_json(
        data: Union[Dict[str, Any], list],
        compression_type: CompressionType = CompressionType.GZIP,
        level: int = 6
    ) -> Dict[str, Any]:
        """
        Compress JSON data and return as dict with metadata.
        
        Args:
            data: JSON-serializable data
            compression_type: Compression algorithm to use
            level: Compression level
        
        Returns:
            Dict with compressed data and metadata
        """
        original_size = len(json.dumps(data).encode('utf-8'))
        compressed = CompressionService.compress(data, compression_type, level)
        compressed_size = len(compressed)
        
        return {
            "compressed": True,
            "compression_type": compression_type.value,
            "data": base64.b64encode(compressed).decode('utf-8'),
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": compressed_size / original_size if original_size > 0 else 0.0,
            "space_saved": original_size - compressed_size
        }
    
    @staticmethod
    def decompress_json(
        compressed_dict: Dict[str, Any]
    ) -> Union[Dict[str, Any], list]:
        """
        Decompress JSON data from compressed dict.
        
        Args:
            compressed_dict: Dict with compressed data and metadata
        
        Returns:
            Decompressed JSON data
        """
        if not compressed_dict.get("compressed"):
            return compressed_dict.get("data", compressed_dict)
        
        compression_type = CompressionType(compressed_dict["compression_type"])
        base64_data = compressed_dict["data"]
        
        decompressed = CompressionService.decompress_from_base64(
            base64_data,
            compression_type
        )
        
        return json.loads(decompressed.decode('utf-8'))
    
    @staticmethod
    def get_compression_stats(
        data: Union[str, bytes, Dict[str, Any], list],
        compression_types: Optional[list] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get compression statistics for different algorithms.
        
        Args:
            data: Data to test compression on
            compression_types: List of compression types to test (default: all)
        
        Returns:
            Dict mapping compression type to stats
        """
        if compression_types is None:
            compression_types = [
                CompressionType.GZIP,
                CompressionType.ZLIB,
                CompressionType.LZMA
            ]
            # Add brotli if available
            try:
                import brotli
                compression_types.append(CompressionType.BROTLI)
            except ImportError:
                pass
        
        # Get original size
        if isinstance(data, (dict, list)):
            original_bytes = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            original_bytes = data.encode('utf-8')
        else:
            original_bytes = data
        
        original_size = len(original_bytes)
        stats = {}
        
        for comp_type in compression_types:
            try:
                compressed = CompressionService.compress(data, comp_type)
                compressed_size = len(compressed)
                
                stats[comp_type.value] = {
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compressed_size / original_size if original_size > 0 else 0.0,
                    "space_saved": original_size - compressed_size,
                    "space_saved_percent": (
                        (original_size - compressed_size) / original_size * 100
                        if original_size > 0 else 0.0
                    )
                }
            except Exception as e:
                stats[comp_type.value] = {
                    "error": str(e)
                }
        
        return stats



