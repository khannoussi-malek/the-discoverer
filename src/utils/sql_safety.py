"""SQL safety utilities."""
import re
from typing import List, Tuple


class SQLSafetyChecker:
    """Check SQL queries for safety."""
    
    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        (r'\bDROP\s+TABLE\b', 'DROP TABLE'),
        (r'\bDELETE\s+FROM\b', 'DELETE'),
        (r'\bTRUNCATE\b', 'TRUNCATE'),
        (r'\bALTER\s+TABLE\b', 'ALTER TABLE'),
        (r'\bCREATE\s+TABLE\b', 'CREATE TABLE'),
        (r'\bDROP\s+DATABASE\b', 'DROP DATABASE'),
        (r'\bGRANT\b', 'GRANT'),
        (r'\bREVOKE\b', 'REVOKE'),
    ]
    
    # Allowed patterns (read-only operations)
    ALLOWED_PATTERNS = [
        r'\bSELECT\b',
        r'\bWITH\b',  # CTE
        r'\bEXPLAIN\b',
        r'\bSHOW\b',
        r'\bDESCRIBE\b',
        r'\bDESC\b',
    ]
    
    @classmethod
    def is_safe(cls, query: str) -> Tuple[bool, List[str]]:
        """
        Check if SQL query is safe to execute.
        
        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        query_upper = query.upper().strip()
        warnings = []
        
        # Check for dangerous patterns
        for pattern, operation in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                warnings.append(f"Dangerous operation detected: {operation}")
                return False, warnings
        
        # Check if query contains at least one allowed pattern
        has_allowed = any(
            re.search(pattern, query_upper, re.IGNORECASE)
            for pattern in cls.ALLOWED_PATTERNS
        )
        
        if not has_allowed:
            warnings.append("Query does not contain any allowed read-only operations")
            return False, warnings
        
        # Check for suspicious patterns
        suspicious = cls._check_suspicious_patterns(query_upper)
        warnings.extend(suspicious)
        
        return True, warnings
    
    @classmethod
    def _check_suspicious_patterns(cls, query: str) -> List[str]:
        """Check for suspicious but not necessarily dangerous patterns."""
        warnings = []
        
        # Check for multiple statements (potential injection)
        if query.count(';') > 1:
            warnings.append("Multiple statements detected - potential SQL injection")
        
        # Check for comments (potential injection)
        if '--' in query or '/*' in query:
            warnings.append("SQL comments detected")
        
        # Check for very long queries
        if len(query) > 10000:
            warnings.append("Very long query detected")
        
        return warnings
    
    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """Basic query sanitization."""
        # Remove null bytes
        sanitized = query.replace('\x00', '')
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Trim
        sanitized = sanitized.strip()
        
        return sanitized

