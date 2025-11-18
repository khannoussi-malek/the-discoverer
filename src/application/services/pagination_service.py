"""Server-side pagination service."""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PaginationParams:
    """Pagination parameters."""
    page: int
    page_size: int
    offset: int
    
    @classmethod
    def create(cls, page: int, page_size: int) -> "PaginationParams":
        """Create pagination params."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 1000:
            page_size = 1000
        
        offset = (page - 1) * page_size
        return cls(page=page, page_size=page_size, offset=offset)


@dataclass
class PaginatedResult:
    """Paginated result."""
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginationService:
    """Server-side pagination service."""
    
    @staticmethod
    def paginate(
        data: List[Dict[str, Any]],
        page: int,
        page_size: int
    ) -> PaginatedResult:
        """Paginate data in memory."""
        params = PaginationParams.create(page, page_size)
        total = len(data)
        
        # Slice data
        paginated_items = data[params.offset:params.offset + params.page_size]
        
        total_pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0
        
        return PaginatedResult(
            items=paginated_items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1
        )
    
    @staticmethod
    def build_sql_pagination(
        query: str,
        page: int,
        page_size: int,
        db_type: str = "postgresql"
    ) -> Tuple[str, int]:
        """Build paginated SQL query."""
        params = PaginationParams.create(page, page_size)
        
        if db_type.lower() in ["postgresql", "mysql"]:
            # Use LIMIT and OFFSET
            paginated_query = f"{query} LIMIT {params.page_size} OFFSET {params.offset}"
        elif db_type.lower() == "sqlite":
            # SQLite also uses LIMIT and OFFSET
            paginated_query = f"{query} LIMIT {params.page_size} OFFSET {params.offset}"
        else:
            # Default to LIMIT/OFFSET
            paginated_query = f"{query} LIMIT {params.page_size} OFFSET {params.offset}"
        
        return paginated_query, params.offset
    
    @staticmethod
    def build_count_query(query: str) -> str:
        """Build count query from SELECT query."""
        # Simple approach: wrap in subquery and count
        # This is a simplified version - could be more sophisticated
        if query.strip().upper().startswith("SELECT"):
            # Remove ORDER BY, LIMIT, OFFSET for count
            query_lower = query.lower()
            
            # Find SELECT ... FROM
            select_match = query_lower.find("select")
            from_match = query_lower.find("from")
            
            if select_match >= 0 and from_match > select_match:
                # Extract FROM clause onwards
                from_clause = query[from_match:]
                
                # Remove ORDER BY, LIMIT, OFFSET
                for clause in ["order by", "limit", "offset"]:
                    idx = from_clause.lower().find(clause)
                    if idx >= 0:
                        # Find end of clause (next keyword or end)
                        end_idx = len(from_clause)
                        for keyword in ["group by", "having", "order by", "limit", "offset"]:
                            next_idx = from_clause.lower().find(keyword, idx + 1)
                            if next_idx >= 0 and next_idx < end_idx:
                                end_idx = next_idx
                        from_clause = from_clause[:idx] + from_clause[end_idx:]
                
                count_query = f"SELECT COUNT(*) as total {from_clause}"
                return count_query
        
        # Fallback
        return f"SELECT COUNT(*) as total FROM ({query}) as subquery"


