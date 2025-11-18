"""Constants."""
from enum import Enum


class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    ELASTICSEARCH = "elasticsearch"
    SQLITE = "sqlite"


class QueryType(str, Enum):
    """Query types."""
    SQL = "sql"
    MONGODB = "mongodb"
    CQL = "cql"
    ELASTICSEARCH = "elasticsearch"


class ChartType(str, Enum):
    """Chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    TABLE = "table"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    SCATTER3D = "scatter3d"
    SURFACE = "surface"
    SUNBURST = "sunburst"
    TREEMAP = "treemap"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    WATERFALL = "waterfall"


class AggregationStrategy(str, Enum):
    """Aggregation strategies."""
    MERGE = "merge"
    JOIN = "join"
    AGGREGATE = "aggregate"


class IndexingStrategy(str, Enum):
    """Content indexing strategies."""
    FULL = "full"
    SAMPLED = "sampled"
    AGGREGATED = "aggregated"
    SMART = "smart"

