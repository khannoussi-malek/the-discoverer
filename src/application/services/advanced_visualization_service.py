"""Advanced visualization service with more chart types and customization."""
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.domain.visualization import Visualization, ChartConfig
from src.core.constants import ChartType


class AdvancedVisualizationService:
    """Advanced visualization service with extended chart types."""
    
    def __init__(self):
        self.base_service = None  # Can reference base VisualizationService
    
    def generate_advanced_chart(
        self,
        data: List[Dict[str, Any]],
        chart_type: str,
        config: Dict[str, Any]
    ) -> Visualization:
        """Generate advanced chart with custom configuration."""
        chart_type_lower = chart_type.lower()
        
        if chart_type_lower == "heatmap":
            return self._create_heatmap(data, config)
        elif chart_type_lower == "box":
            return self._create_box_plot(data, config)
        elif chart_type_lower == "violin":
            return self._create_violin_plot(data, config)
        elif chart_type_lower == "scatter3d":
            return self._create_3d_scatter(data, config)
        elif chart_type_lower == "surface":
            return self._create_surface_plot(data, config)
        elif chart_type_lower == "sunburst":
            return self._create_sunburst(data, config)
        elif chart_type_lower == "treemap":
            return self._create_treemap(data, config)
        elif chart_type_lower == "funnel":
            return self._create_funnel(data, config)
        elif chart_type_lower == "gauge":
            return self._create_gauge(data, config)
        elif chart_type_lower == "waterfall":
            return self._create_waterfall(data, config)
        else:
            # Fallback to basic chart types
            return self._create_basic_chart(data, chart_type, config)
    
    def _create_heatmap(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create heatmap chart."""
        df = pd.DataFrame(data)
        
        x_col = config.get("x_axis", df.columns[0] if len(df.columns) > 0 else "x")
        y_col = config.get("y_axis", df.columns[1] if len(df.columns) > 1 else "y")
        z_col = config.get("z_axis", df.columns[2] if len(df.columns) > 2 else "value")
        
        # Pivot for heatmap
        if x_col in df.columns and y_col in df.columns and z_col in df.columns:
            pivot = df.pivot_table(values=z_col, index=y_col, columns=x_col, aggfunc='mean')
            fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index))
        else:
            # Simple heatmap from first numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns[:3]
            if len(numeric_cols) >= 2:
                fig = go.Figure(data=go.Heatmap(z=df[numeric_cols[2]].values if len(numeric_cols) > 2 else None,
                                                x=df[numeric_cols[0]].values,
                                                y=df[numeric_cols[1]].values))
            else:
                fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Heatmap"))
        chart_config = ChartConfig(
            chart_type="heatmap",
            title=config.get("title", "Heatmap")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_box_plot(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create box plot."""
        df = pd.DataFrame(data)
        
        x_col = config.get("x_axis")
        y_col = config.get("y_axis", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else None)
        
        if x_col and y_col and x_col in df.columns and y_col in df.columns:
            fig = px.box(df, x=x_col, y=y_col)
        elif y_col and y_col in df.columns:
            fig = px.box(df, y=y_col)
        else:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                fig = px.box(df, y=numeric_cols[0])
            else:
                fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Box Plot"))
        chart_config = ChartConfig(
            chart_type="box",
            title=config.get("title", "Box Plot")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_violin_plot(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create violin plot."""
        df = pd.DataFrame(data)
        
        x_col = config.get("x_axis")
        y_col = config.get("y_axis", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else None)
        
        if x_col and y_col and x_col in df.columns and y_col in df.columns:
            fig = px.violin(df, x=x_col, y=y_col)
        elif y_col and y_col in df.columns:
            fig = px.violin(df, y=y_col)
        else:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                fig = px.violin(df, y=numeric_cols[0])
            else:
                fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Violin Plot"))
        chart_config = ChartConfig(
            chart_type="violin",
            title=config.get("title", "Violin Plot")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_3d_scatter(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create 3D scatter plot."""
        df = pd.DataFrame(data)
        
        x_col = config.get("x_axis", df.columns[0] if len(df.columns) > 0 else "x")
        y_col = config.get("y_axis", df.columns[1] if len(df.columns) > 1 else "y")
        z_col = config.get("z_axis", df.columns[2] if len(df.columns) > 2 else "z")
        
        if all(col in df.columns for col in [x_col, y_col, z_col]):
            fig = px.scatter_3d(df, x=x_col, y=y_col, z=z_col)
        else:
            fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "3D Scatter Plot"))
        chart_config = ChartConfig(
            chart_type="scatter3d",
            title=config.get("title", "3D Scatter Plot")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_surface_plot(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create surface plot."""
        df = pd.DataFrame(data)
        
        # Need at least 3 numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns[:3]
        
        if len(numeric_cols) >= 3:
            # Create surface from data
            fig = go.Figure(data=[go.Surface(
                z=df[numeric_cols[2]].values.reshape(-1, 10) if len(df) > 10 else df[numeric_cols[2]].values,
                x=df[numeric_cols[0]].values,
                y=df[numeric_cols[1]].values
            )])
        else:
            fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Surface Plot"))
        chart_config = ChartConfig(
            chart_type="surface",
            title=config.get("title", "Surface Plot")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_sunburst(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create sunburst chart."""
        df = pd.DataFrame(data)
        
        # Sunburst needs hierarchical data
        path_cols = config.get("path", [col for col in df.columns[:3]])
        value_col = config.get("value", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else None)
        
        if path_cols and value_col:
            fig = px.sunburst(df, path=path_cols, values=value_col)
        else:
            fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Sunburst Chart"))
        chart_config = ChartConfig(
            chart_type="sunburst",
            title=config.get("title", "Sunburst Chart")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_treemap(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create treemap chart."""
        df = pd.DataFrame(data)
        
        path_cols = config.get("path", [col for col in df.columns[:2]])
        value_col = config.get("value", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else None)
        
        if path_cols and value_col:
            fig = px.treemap(df, path=path_cols, values=value_col)
        else:
            fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Treemap"))
        chart_config = ChartConfig(
            chart_type="treemap",
            title=config.get("title", "Treemap")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_funnel(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create funnel chart."""
        df = pd.DataFrame(data)
        
        x_col = config.get("x_axis", df.columns[0] if len(df.columns) > 0 else "stage")
        y_col = config.get("y_axis", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else "value")
        
        if x_col in df.columns and y_col in df.columns:
            fig = go.Figure(go.Funnel(
                y=df[x_col].values,
                x=df[y_col].values
            ))
        else:
            fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Funnel Chart"))
        chart_config = ChartConfig(
            chart_type="funnel",
            title=config.get("title", "Funnel Chart")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_gauge(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create gauge chart."""
        df = pd.DataFrame(data)
        
        value_col = config.get("value", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else None)
        value = df[value_col].iloc[0] if value_col and value_col in df.columns and len(df) > 0 else 0
        
        min_val = config.get("min", 0)
        max_val = config.get("max", 100)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': config.get("title", "Gauge")},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [min_val, max_val * 0.5], 'color': "lightgray"},
                    {'range': [max_val * 0.5, max_val], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_val * 0.9
                }
            }
        ))
        
        chart_config = ChartConfig(
            chart_type="gauge",
            title=config.get("title", "Gauge")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_waterfall(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> Visualization:
        """Create waterfall chart."""
        df = pd.DataFrame(data)
        
        x_col = config.get("x_axis", df.columns[0] if len(df.columns) > 0 else "category")
        y_col = config.get("y_axis", df.select_dtypes(include=['number']).columns[0] if len(df.columns) > 0 else "value")
        
        if x_col in df.columns and y_col in df.columns:
            fig = go.Figure(go.Waterfall(
                name="Waterfall",
                orientation="v",
                measure=config.get("measure", ["relative"] * len(df)),
                x=df[x_col].values,
                textposition="outside",
                text=df[y_col].values,
                y=df[y_col].values,
                connector={"line": {"color": "rgb(63, 63, 63)"}}
            ))
        else:
            fig = go.Figure()
        
        fig.update_layout(title=config.get("title", "Waterfall Chart"))
        chart_config = ChartConfig(
            chart_type="waterfall",
            title=config.get("title", "Waterfall Chart")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data=fig.to_dict(),
            format="json"
        )
    
    def _create_basic_chart(self, data: List[Dict[str, Any]], chart_type: str, config: Dict[str, Any]) -> Visualization:
        """Fallback to basic chart creation."""
        # This would delegate to the base VisualizationService
        # For now, return a simple visualization
        chart_config = ChartConfig(
            chart_type=chart_type,
            title=config.get("title", "Chart")
        )
        return Visualization(
            query_id="",
            chart_config=chart_config,
            data={"data": data},
            format="json"
        )

