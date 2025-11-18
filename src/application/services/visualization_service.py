"""Visualization service - Chart generation."""
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from src.domain.visualization import Visualization, ChartConfig
from src.domain.result import AggregatedResult

# Lazy imports for optional dependencies
if TYPE_CHECKING:
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
else:
    go = None
    px = None
    pd = None


class VisualizationService:
    """Visualization service - KISS: One responsibility."""
    
    def _ensure_dependencies(self):
        """Ensure plotly and pandas are available."""
        global go, px, pd
        if go is None or px is None or pd is None:
            try:
                import plotly.graph_objects as go
                import plotly.express as px
                import pandas as pd
                globals()['go'] = go
                globals()['px'] = px
                globals()['pd'] = pd
            except ImportError:
                raise ImportError("plotly and pandas are required for visualization. Install with: pip install plotly pandas")
    
    def generate_chart(
        self,
        result: AggregatedResult,
        chart_config: Optional[ChartConfig] = None
    ) -> Visualization:
        """Generate chart from query result."""
        self._ensure_dependencies()
        if not chart_config:
            chart_config = self._detect_chart_type(result)
        
        # Convert data to DataFrame for easier manipulation
        df = pd.DataFrame(result.merged_data)
        
        # Generate chart based on type
        if chart_config.chart_type == "bar":
            chart_data = self._create_bar_chart(df, chart_config)
        elif chart_config.chart_type == "line":
            chart_data = self._create_line_chart(df, chart_config)
        elif chart_config.chart_type == "pie":
            chart_data = self._create_pie_chart(df, chart_config)
        elif chart_config.chart_type == "scatter":
            chart_data = self._create_scatter_chart(df, chart_config)
        else:
            chart_data = self._create_table(df, chart_config)
        
        return Visualization(
            query_id="",  # Will be set by caller
            chart_config=chart_config,
            data=chart_data,
            format="json"
        )
    
    def _detect_chart_type(self, result: AggregatedResult) -> ChartConfig:
        """Auto-detect appropriate chart type."""
        if not result.merged_data:
            return ChartConfig(chart_type="table", title="No Data")
        
        df = pd.DataFrame(result.merged_data)
        
        # Simple heuristics
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            return ChartConfig(
                chart_type="scatter",
                x_axis=numeric_cols[0],
                y_axis=numeric_cols[1],
                title="Data Visualization"
            )
        elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            return ChartConfig(
                chart_type="bar",
                x_axis=categorical_cols[0],
                y_axis=numeric_cols[0],
                title="Data Visualization"
            )
        else:
            return ChartConfig(chart_type="table", title="Data Table")
    
    def _create_bar_chart(
        self,
        df: Any,
        config: ChartConfig
    ) -> Dict[str, Any]:
        """Create bar chart."""
        if config.x_axis and config.y_axis:
            fig = px.bar(
                df,
                x=config.x_axis,
                y=config.y_axis,
                title=config.title
            )
        else:
            # Use first two columns
            cols = df.columns.tolist()
            if len(cols) >= 2:
                fig = px.bar(df, x=cols[0], y=cols[1], title=config.title)
            else:
                fig = px.bar(df, title=config.title)
        
        return fig.to_dict()
    
    def _create_line_chart(
        self,
        df: Any,
        config: ChartConfig
    ) -> Dict[str, Any]:
        """Create line chart."""
        if config.x_axis and config.y_axis:
            fig = px.line(
                df,
                x=config.x_axis,
                y=config.y_axis,
                title=config.title
            )
        else:
            cols = df.columns.tolist()
            if len(cols) >= 2:
                fig = px.line(df, x=cols[0], y=cols[1], title=config.title)
            else:
                fig = px.line(df, title=config.title)
        
        return fig.to_dict()
    
    def _create_pie_chart(
        self,
        df: Any,
        config: ChartConfig
    ) -> Dict[str, Any]:
        """Create pie chart."""
        if config.x_axis and config.y_axis:
            fig = px.pie(
                df,
                names=config.x_axis,
                values=config.y_axis,
                title=config.title
            )
        else:
            cols = df.columns.tolist()
            if len(cols) >= 2:
                fig = px.pie(df, names=cols[0], values=cols[1], title=config.title)
            else:
                fig = px.pie(df, title=config.title)
        
        return fig.to_dict()
    
    def _create_scatter_chart(
        self,
        df: Any,
        config: ChartConfig
    ) -> Dict[str, Any]:
        """Create scatter chart."""
        if config.x_axis and config.y_axis:
            fig = px.scatter(
                df,
                x=config.x_axis,
                y=config.y_axis,
                title=config.title
            )
        else:
            cols = df.columns.tolist()
            if len(cols) >= 2:
                fig = px.scatter(df, x=cols[0], y=cols[1], title=config.title)
            else:
                fig = px.scatter(df, title=config.title)
        
        return fig.to_dict()
    
    def _create_table(
        self,
        df: Any,
        config: ChartConfig
    ) -> Dict[str, Any]:
        """Create table visualization."""
        return {
            "type": "table",
            "data": df.to_dict("records"),
            "columns": df.columns.tolist()
        }

