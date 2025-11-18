"""Query result streaming utilities."""
from typing import AsyncIterator, Dict, Any, List, Optional
from enum import Enum
import json
import csv
from io import StringIO


class StreamingFormat(str, Enum):
    """Streaming format types."""
    NDJSON = "ndjson"  # Newline-delimited JSON
    JSON = "json"  # JSON array
    CSV = "csv"  # CSV format
    TSV = "tsv"  # Tab-separated values


class QueryResultStreamer:
    """Stream query results in various formats."""
    
    def __init__(self, format: StreamingFormat = StreamingFormat.NDJSON):
        self.format = format
    
    async def stream_results(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Stream results in the specified format.
        
        Args:
            results: Async iterator of result rows
            metadata: Optional metadata to include
        
        Yields:
            Formatted data chunks
        """
        if self.format == StreamingFormat.NDJSON:
            async for chunk in self._stream_ndjson(results, metadata):
                yield chunk
        elif self.format == StreamingFormat.JSON:
            async for chunk in self._stream_json(results, metadata):
                yield chunk
        elif self.format == StreamingFormat.CSV:
            async for chunk in self._stream_csv(results, metadata):
                yield chunk
        elif self.format == StreamingFormat.TSV:
            async for chunk in self._stream_tsv(results, metadata):
                yield chunk
    
    async def _stream_ndjson(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Stream as NDJSON (newline-delimited JSON)."""
        # Send metadata first if provided
        if metadata:
            yield json.dumps(metadata) + "\n"
        
        # Stream data rows
        async for row in results:
            yield json.dumps(row) + "\n"
    
    async def _stream_json(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Stream as JSON array."""
        yield "[\n"
        
        first = True
        async for row in results:
            if not first:
                yield ",\n"
            yield json.dumps(row)
            first = False
        
        yield "\n]"
    
    async def _stream_csv(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Stream as CSV."""
        output = StringIO()
        writer = None
        first_row = True
        
        async for row in results:
            if first_row:
                # Initialize CSV writer with headers
                if row:
                    writer = csv.DictWriter(output, fieldnames=row.keys())
                    writer.writeheader()
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)
                first_row = False
            
            if writer:
                writer.writerow(row)
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
    
    async def _stream_tsv(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Stream as TSV (tab-separated values)."""
        output = StringIO()
        writer = None
        first_row = True
        
        async for row in results:
            if first_row:
                # Initialize TSV writer with headers
                if row:
                    writer = csv.DictWriter(
                        output,
                        fieldnames=row.keys(),
                        delimiter='\t'
                    )
                    writer.writeheader()
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)
                first_row = False
            
            if writer:
                writer.writerow(row)
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)


class ChunkedResultStreamer:
    """Stream results in chunks for better performance."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        format: StreamingFormat = StreamingFormat.NDJSON
    ):
        self.chunk_size = chunk_size
        self.format = format
        self.streamer = QueryResultStreamer(format)
    
    async def stream_chunked(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Stream results in chunks.
        
        Args:
            results: Async iterator of result rows
            metadata: Optional metadata
        
        Yields:
            Chunked data
        """
        chunk = []
        async for row in results:
            chunk.append(row)
            
            if len(chunk) >= self.chunk_size:
                # Stream chunk
                async for data in self.streamer.stream_results(
                    self._list_to_async_iterator(chunk),
                    None  # Don't send metadata for each chunk
                ):
                    yield data
                chunk = []
        
        # Stream remaining rows
        if chunk:
            async for data in self.streamer.stream_results(
                self._list_to_async_iterator(chunk),
                None
            ):
                yield data
    
    async def _list_to_async_iterator(
        self,
        items: List[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Convert list to async iterator."""
        for item in items:
            yield item


class ProgressStreamer:
    """Stream results with progress updates."""
    
    def __init__(
        self,
        total_rows: Optional[int] = None,
        format: StreamingFormat = StreamingFormat.NDJSON
    ):
        self.total_rows = total_rows
        self.format = format
        self.streamer = QueryResultStreamer(format)
        self.rows_streamed = 0
    
    async def stream_with_progress(
        self,
        results: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Stream results with progress updates.
        
        Args:
            results: Async iterator of result rows
            metadata: Optional metadata
        
        Yields:
            Data with progress updates
        """
        # Send initial metadata with progress info
        if metadata:
            metadata["progress"] = {
                "total": self.total_rows,
                "streamed": 0,
                "percentage": 0.0
            }
            yield json.dumps(metadata) + "\n"
        
        # Stream data with periodic progress updates
        async for row in results:
            self.rows_streamed += 1
            
            # Send progress update every 100 rows or at milestones
            if self.total_rows and (
                self.rows_streamed % 100 == 0 or
                self.rows_streamed == self.total_rows or
                self.rows_streamed in [10, 50, 100, 500, 1000, 5000, 10000]
            ):
                progress = {
                    "type": "progress",
                    "streamed": self.rows_streamed,
                    "total": self.total_rows,
                    "percentage": (
                        (self.rows_streamed / self.total_rows * 100)
                        if self.total_rows else 0.0
                    )
                }
                yield json.dumps(progress) + "\n"
            
            # Stream actual row
            yield json.dumps(row) + "\n"
        
        # Send completion progress
        if self.total_rows:
            progress = {
                "type": "progress",
                "streamed": self.rows_streamed,
                "total": self.total_rows,
                "percentage": 100.0,
                "complete": True
            }
            yield json.dumps(progress) + "\n"



