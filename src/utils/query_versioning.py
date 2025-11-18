"""Query versioning utilities."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid
import hashlib


@dataclass
class QueryVersion:
    """Query version entity."""
    id: str
    query_id: str
    version: int
    query_text: str
    generated_query: str
    result_hash: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    notes: Optional[str] = None
    is_current: bool = False


class QueryVersionManager:
    """Manage query versions."""
    
    def __init__(self):
        self._versions: Dict[str, List[QueryVersion]] = {}  # query_id -> versions
    
    def _hash_result(self, result: Dict[str, Any]) -> str:
        """Generate hash for query result."""
        import json
        result_str = json.dumps(result, sort_keys=True, default=str)
        return hashlib.sha256(result_str.encode()).hexdigest()
    
    async def create_version(
        self,
        query_id: str,
        query_text: str,
        generated_query: str,
        result: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> QueryVersion:
        """Create a new version of a query."""
        # Get existing versions
        versions = self._versions.get(query_id, [])
        
        # Mark all previous versions as not current
        for v in versions:
            v.is_current = False
        
        # Create new version
        version_num = len(versions) + 1
        result_hash = self._hash_result(result) if result else None
        
        version = QueryVersion(
            id=str(uuid.uuid4()),
            query_id=query_id,
            version=version_num,
            query_text=query_text,
            generated_query=generated_query,
            result_hash=result_hash,
            created_at=datetime.utcnow(),
            created_by=created_by,
            notes=notes,
            is_current=True
        )
        
        versions.append(version)
        self._versions[query_id] = versions
        
        return version
    
    async def get_versions(self, query_id: str) -> List[QueryVersion]:
        """Get all versions of a query."""
        return self._versions.get(query_id, [])
    
    async def get_current_version(self, query_id: str) -> Optional[QueryVersion]:
        """Get current version of a query."""
        versions = self._versions.get(query_id, [])
        for version in versions:
            if version.is_current:
                return version
        return versions[-1] if versions else None
    
    async def get_version(self, query_id: str, version: int) -> Optional[QueryVersion]:
        """Get specific version of a query."""
        versions = self._versions.get(query_id, [])
        for v in versions:
            if v.version == version:
                return v
        return None
    
    async def set_current_version(self, query_id: str, version: int) -> bool:
        """Set a specific version as current."""
        versions = self._versions.get(query_id, [])
        
        # Mark all as not current
        for v in versions:
            v.is_current = False
        
        # Set specified version as current
        for v in versions:
            if v.version == version:
                v.is_current = True
                return True
        
        return False
    
    async def compare_versions(
        self,
        query_id: str,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """Compare two versions of a query."""
        v1 = await self.get_version(query_id, version1)
        v2 = await self.get_version(query_id, version2)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        return {
            "query_id": query_id,
            "version1": {
                "version": v1.version,
                "query_text": v1.query_text,
                "generated_query": v1.generated_query,
                "result_hash": v1.result_hash,
                "created_at": v1.created_at.isoformat()
            },
            "version2": {
                "version": v2.version,
                "query_text": v2.query_text,
                "generated_query": v2.generated_query,
                "result_hash": v2.result_hash,
                "created_at": v2.created_at.isoformat()
            },
            "differences": {
                "query_text_changed": v1.query_text != v2.query_text,
                "generated_query_changed": v1.generated_query != v2.generated_query,
                "result_changed": v1.result_hash != v2.result_hash
            }
        }


