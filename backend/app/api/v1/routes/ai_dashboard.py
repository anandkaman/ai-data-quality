from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Optional, Union
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.models.database_models import DatasetMetadata
from app.services.llm_engine.ollama_client import OllamaClient
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

router = APIRouter()

# Define all supported chart types
SUPPORTED_CHART_TYPES = {
    'histogram': 'Distribution of a single numeric variable',
    'scatter': 'Relationship between two numeric variables',
    'bar': 'Comparison of categorical data',
    'box': 'Statistical distribution with quartiles',
    'violin': 'Distribution shape with density',
    'heatmap': 'Correlation matrix visualization',
    'line': 'Trends over continuous data',
    'pie': 'Proportional composition',
    'area': 'Cumulative trends',
    'bubble': '3D scatter with size variable',
    'density_contour': 'Density distribution',
    'density_heatmap': '2D concentration',
    'sunburst': 'Hierarchical circles',
    'treemap': 'Hierarchical rectangles',
    'funnel': 'Sequential reduction',
    'waterfall': 'Cumulative changes',
    'parallel_coordinates': 'Multivariate relationships',
    'parallel_categories': 'Categorical flow',
    'strip': 'Individual data points',
    'qqplot': 'Distribution comparison',
    'ecdf': 'Cumulative distribution',
    '3d_scatter': '3D relationship',
    'metric_card': 'Simple statistic display (count, sum, avg, min, max)'
}

class DashboardRequest(BaseModel):
    dataset_id: int
    num_columns: int
    prompt: Optional[str] = None

class MetricCard(BaseModel):
    metric_type: str
    column: str
    value: Union[int, float, str]
    title: str
    description: str

class ChartData(BaseModel):
    type: str
    title: str
    plotly_json: Optional[str] = None
    description: str
    color_scheme: Optional[str] = None
    metric_card: Optional[MetricCard] = None

class DashboardResponse(BaseModel):
    items: List[ChartData]
    num_columns: int
    analysis: str
    dashboard_id: str

ollama_client = OllamaClient()

@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard(request: DashboardRequest, db: Session = Depends(get_db)):
    """Generate AI-powered dashboard with charts and metric cards"""
    
    dataset = db.query(DatasetMetadata).filter(DatasetMetadata.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = os.path.join(settings.UPLOAD_DIR, dataset.filename)
    
    if dataset.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    sample_data = df.head(10)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    chart_types_description = "\n".join([f"  - {k}: {v}" for k, v in SUPPORTED_CHART_TYPES.items()])
    
    system_prompt = f"""You are an expert data visualization analyst.

AVAILABLE VISUALIZATION TYPES:
{chart_types_description}

IMPORTANT GUIDELINES:
1. For simple statistics (totals, averages, counts), use 'metric_card' instead of charts
2. Use charts for patterns, distributions, relationships, and trends
3. Mix metric cards and charts for comprehensive analysis
4. Generate as many visualizations as needed to tell the complete story (not limited to fixed number)
5. Prioritize user's explicit requests
6. Use diverse chart types

Respond in valid JSON format only."""
    
    user_preference = request.prompt or "Provide comprehensive analysis with key metrics and visualizations"
    
    prompt = f"""Dataset Information:
Name: {dataset.filename}
Rows: {len(df)} | Columns: {len(df.columns)}

Column Details:
{json.dumps({col: {
    'type': str(df[col].dtype), 
    'unique': int(df[col].nunique()), 
    'missing': int(df[col].isnull().sum()),
    'sample': df[col].dropna().head(3).tolist()
} for col in df.columns}, indent=2)}

Numeric: {', '.join(numeric_cols)}
Categorical: {', '.join(categorical_cols)}

First 10 Rows:
{sample_data.to_string()}

Stats:
{df[numeric_cols].describe().to_string() if numeric_cols else 'No numeric columns'}

USER REQUEST: "{user_preference}"

TASK: Generate comprehensive dashboard items (metric cards + charts).

For METRIC CARDS, use format:
{{
  "type": "metric_card",
  "metric_type": "count|sum|avg|min|max|median",
  "column": "column_name",
  "title": "Clear Title",
  "description": "What this metric means"
}}

For CHARTS, use format:
{{
  "type": "histogram|scatter|bar|etc",
  "x_column": "column_name",
  "y_column": "column_name or null",
  "z_column": "column_name or null",
  "color_scheme": "viridis|blues|reds|etc",
  "title": "Descriptive Title",
  "description": "What insights this reveals"
}}

RESPOND WITH JSON ARRAY:
[
  // Mix of metric cards and charts
  // Generate as many as needed (typically 5-12 items)
  // Start with key metrics, then visualizations
]

EXAMPLES:
- Total Sales: metric_card with sum
- Average Revenue: metric_card with avg
- Customer Count: metric_card with count
- Sales Distribution: histogram chart
- Category Breakdown: bar or pie chart
"""
    
    try:
        result = await ollama_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=3500
        )
        
        response_text = result.get('response', '')
        
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        
        if json_match:
            suggestions = json.loads(json_match.group())
        else:
            suggestions = generate_fallback_suggestions(df, numeric_cols, categorical_cols, user_preference)
        
        items = []
        for suggestion in suggestions:
            try:
                if suggestion.get('type') == 'metric_card':
                    metric = generate_metric_card(df, suggestion)
                    items.append(ChartData(
                        type='metric_card',
                        title=suggestion['title'],
                        plotly_json=None,
                        description=suggestion.get('description', ''),
                        metric_card=metric
                    ))
                else:
                    chart_fig = generate_plotly_chart(df, suggestion, categorical_cols)
                    items.append(ChartData(
                        type=suggestion['type'],
                        title=suggestion['title'],
                        plotly_json=chart_fig.to_json(),
                        description=suggestion.get('description', ''),
                        color_scheme=suggestion.get('color_scheme', 'viridis'),
                        metric_card=None
                    ))
            except Exception as e:
                print(f"Failed to generate item {suggestion.get('type', 'unknown')}: {e}")
                continue
        
        analysis_prompt = f"""Dataset: {len(df)} rows, {len(df.columns)} columns
User: "{user_preference}"
Generated {len(items)} items ({sum(1 for i in items if i.type == 'metric_card')} metrics, {sum(1 for i in items if i.type != 'metric_card')} charts)

Provide 4-5 sentence analysis covering:
1. Key findings from metrics and visualizations
2. How they address user's request
3. Notable patterns or insights
4. Actionable recommendations"""
        
        analysis_result = await ollama_client.generate(
            prompt=analysis_prompt,
            system_prompt="Senior data analyst. Clear, actionable insights.",
            temperature=0.6,
            max_tokens=400
        )
        
        dashboard_id = f"dashboard_{request.dataset_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return DashboardResponse(
            items=items,
            num_columns=request.num_columns,
            analysis=analysis_result.get('response', ''),
            dashboard_id=dashboard_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

def generate_metric_card(df, suggestion):
    """Generate metric card with calculated value"""
    
    metric_type = suggestion.get('metric_type', 'count')
    column = suggestion.get('column')
    
    try:
        if metric_type == 'count':
            if column:
                value = int(df[column].count())
            else:
                value = len(df)
        elif metric_type == 'sum':
            value = float(df[column].sum())
        elif metric_type == 'avg' or metric_type == 'mean':
            value = float(df[column].mean())
        elif metric_type == 'min':
            value = float(df[column].min())
        elif metric_type == 'max':
            value = float(df[column].max())
        elif metric_type == 'median':
            value = float(df[column].median())
        else:
            value = len(df)
        
        # Format value
        if isinstance(value, float):
            if value > 1000000:
                formatted_value = f"{value/1000000:.2f}M"
            elif value > 1000:
                formatted_value = f"{value/1000:.2f}K"
            else:
                formatted_value = f"{value:.2f}"
        else:
            if value > 1000000:
                formatted_value = f"{value/1000000:.1f}M"
            elif value > 1000:
                formatted_value = f"{value/1000:.1f}K"
            else:
                formatted_value = str(value)
        
        return MetricCard(
            metric_type=metric_type,
            column=column or 'dataset',
            value=formatted_value,
            title=suggestion.get('title', f'{metric_type.title()} of {column}'),
            description=suggestion.get('description', '')
        )
    
    except Exception as e:
        print(f"Metric card error: {e}")
        return MetricCard(
            metric_type=metric_type,
            column=column or 'unknown',
            value='N/A',
            title=suggestion.get('title', 'Metric'),
            description='Could not calculate'
        )

def generate_plotly_chart(df, suggestion, categorical_cols=None):
    """Generate interactive Plotly chart with expanded chart types"""
    
    chart_type = suggestion['type']
    x_col = suggestion.get('x_column')
    y_col = suggestion.get('y_column')
    z_col = suggestion.get('z_column')
    color_scheme = suggestion.get('color_scheme', 'viridis')
    title = suggestion['title']
    
    if categorical_cols is None:
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    color_palettes = {
        'viridis': px.colors.sequential.Viridis,
        'blues': px.colors.sequential.Blues,
        'reds': px.colors.sequential.Reds,
        'greens': px.colors.sequential.Greens,
        'plasma': px.colors.sequential.Plasma,
        'rainbow': px.colors.qualitative.Bold,
        'turbo': px.colors.sequential.Turbo,
        'sunset': px.colors.sequential.Sunset
    }
    
    colors_to_use = color_palettes.get(color_scheme.lower(), px.colors.sequential.Viridis)
    
    try:
        if chart_type == 'histogram':
            clean_data = df[x_col].replace([np.inf, -np.inf], np.nan).dropna()
            if len(clean_data) == 0:
                raise ValueError(f"No valid data in {x_col}")
            fig = px.histogram(df[df[x_col].notna()], x=x_col, title=title, color_discrete_sequence=colors_to_use, nbins=min(30, len(clean_data) // 5))
            fig.update_traces(marker_line_width=1, marker_line_color="white")
            
        elif chart_type == 'scatter':
            can_add_trendline = False
            if y_col and x_col in df.columns and y_col in df.columns:
                if df[x_col].dtype in ['int64', 'float64'] and df[y_col].dtype in ['int64', 'float64']:
                    valid_data = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
                    if len(valid_data) >= 3:
                        if valid_data[x_col].var() > 1e-10 and valid_data[y_col].var() > 1e-10:
                            can_add_trendline = True
            try:
                fig = px.scatter(df, x=x_col, y=y_col, title=title, color_discrete_sequence=colors_to_use, trendline="ols" if can_add_trendline else None)
            except:
                fig = px.scatter(df, x=x_col, y=y_col, title=title, color_discrete_sequence=colors_to_use)
            
        elif chart_type == 'bar':
            value_counts = df[x_col].value_counts().head(15)
            fig = px.bar(x=value_counts.index, y=value_counts.values, title=title, labels={'x': x_col, 'y': 'Count'}, color=value_counts.values, color_continuous_scale=color_scheme)
            
        elif chart_type == 'box':
            fig = px.box(df[df[x_col].notna()], y=x_col, title=title, color_discrete_sequence=colors_to_use)
            
        elif chart_type == 'violin':
            fig = px.violin(df[df[x_col].notna()], y=x_col, title=title, box=True, color_discrete_sequence=colors_to_use)
            
        elif chart_type == 'heatmap':
            numeric_df = df.select_dtypes(include=['number']).replace([np.inf, -np.inf], np.nan).dropna(axis=1, how='all')
            correlation = numeric_df.corr()
            fig = px.imshow(correlation, title=title, color_continuous_scale=color_scheme, text_auto='.2f', aspect='auto')
        
        elif chart_type == 'line':
            clean_df = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna() if y_col else df[[x_col]].replace([np.inf, -np.inf], np.nan).dropna()
            fig = px.line(clean_df, x=clean_df.index if x_col == 'index' else x_col, y=y_col if y_col else x_col, title=title, color_discrete_sequence=colors_to_use)
            
        elif chart_type == 'pie':
            value_counts = df[x_col].value_counts().head(10)
            fig = px.pie(values=value_counts.values, names=value_counts.index, title=title, color_discrete_sequence=colors_to_use)
        
        elif chart_type == 'area':
            clean_df = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
            fig = px.area(clean_df, x=x_col, y=y_col, title=title, color_discrete_sequence=colors_to_use)
            
        elif chart_type == 'bubble':
            if z_col:
                clean_df = df[[x_col, y_col, z_col]].replace([np.inf, -np.inf], np.nan).dropna()
                fig = px.scatter(clean_df, x=x_col, y=y_col, size=z_col, title=title, color_discrete_sequence=colors_to_use)
            else:
                fig = px.scatter(df, x=x_col, y=y_col, title=title)
        
        elif chart_type == 'density_contour':
            clean_df = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
            fig = px.density_contour(clean_df, x=x_col, y=y_col, title=title, color_discrete_sequence=colors_to_use)
            fig.update_traces(contours_coloring="fill", contours_showlabels=True)
            
        elif chart_type == 'density_heatmap':
            clean_df = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
            fig = px.density_heatmap(clean_df, x=x_col, y=y_col, title=title, color_continuous_scale=color_scheme)
        
        elif chart_type == 'sunburst':
            if y_col:
                fig = px.sunburst(df[[x_col, y_col]].dropna(), path=[x_col, y_col], title=title, color_discrete_sequence=colors_to_use)
            else:
                value_counts = df[x_col].value_counts()
                fig = px.sunburst(names=value_counts.index, values=value_counts.values, title=title)
        
        elif chart_type == 'treemap':
            if y_col:
                fig = px.treemap(df[[x_col, y_col]].dropna(), path=[x_col, y_col], title=title, color_discrete_sequence=colors_to_use)
            else:
                value_counts = df[x_col].value_counts()
                fig = px.treemap(names=value_counts.index, values=value_counts.values, title=title)
        
        elif chart_type == 'funnel':
            value_counts = df[x_col].value_counts().head(10)
            fig = px.funnel(y=value_counts.index, x=value_counts.values, title=title, color_discrete_sequence=colors_to_use)
        
        elif chart_type == 'waterfall':
            if y_col:
                clean_df = df[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna().head(20)
                fig = go.Figure(go.Waterfall(x=clean_df[x_col], y=clean_df[y_col], name=title))
                fig.update_layout(title=title)
            else:
                fig = go.Figure()
                fig.update_layout(title=f"{title} (requires x and y columns)")
        
        elif chart_type == 'parallel_coordinates':
            numeric_df = df.select_dtypes(include=['number']).replace([np.inf, -np.inf], np.nan).dropna().head(100)
            fig = px.parallel_coordinates(numeric_df, title=title, color_continuous_scale=color_scheme)
        
        elif chart_type == 'parallel_categories':
            if len(categorical_cols) >= 2:
                cat_df = df[categorical_cols[:4]].dropna().head(100)
                fig = px.parallel_categories(cat_df, title=title, color_continuous_scale=color_scheme)
        
        elif chart_type == 'strip':
            clean_df = df[[x_col, y_col if y_col else x_col]].replace([np.inf, -np.inf], np.nan).dropna()
            fig = px.strip(clean_df, x=x_col, y=y_col if y_col else x_col, title=title, color_discrete_sequence=colors_to_use)
        
        elif chart_type == 'qqplot':
            data = df[x_col].replace([np.inf, -np.inf], np.nan).dropna()
            qq = stats.probplot(data, dist="norm")
            fig = go.Figure()
            fig.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers', name='Data')
            fig.add_scatter(x=qq[0][0], y=qq[0][0] * qq[1][0] + qq[1][1], mode='lines', name='Fit', line=dict(color='red'))
            fig.update_layout(title=title, xaxis_title='Theoretical Quantiles', yaxis_title='Sample Quantiles')
        
        elif chart_type == 'ecdf':
            data = df[x_col].replace([np.inf, -np.inf], np.nan).dropna()
            data_sorted = np.sort(data)
            ecdf = np.arange(1, len(data_sorted) + 1) / len(data_sorted)
            fig = go.Figure(go.Scatter(x=data_sorted, y=ecdf, mode='lines'))
            fig.update_layout(title=title, xaxis_title=x_col, yaxis_title='ECDF')
        
        elif chart_type == '3d_scatter':
            if y_col and z_col:
                clean_df = df[[x_col, y_col, z_col]].replace([np.inf, -np.inf], np.nan).dropna()
                fig = px.scatter_3d(clean_df, x=x_col, y=y_col, z=z_col, title=title, color_discrete_sequence=colors_to_use)
            else:
                fig = go.Figure()
                fig.update_layout(title=f"{title} (requires x, y, z columns)")
        
        else:
            fig = px.histogram(df[df[x_col].notna()], x=x_col, title=f"{title} (fallback)")
        
        fig.update_layout(
            hovermode='closest',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            plot_bgcolor='rgba(240,240,240,0.5)',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            height=450,
            margin=dict(l=50, r=30, t=60, b=50)
        )
        
        return fig
    
    except Exception as e:
        print(f"Chart generation error for {chart_type}: {e}")
        fig = go.Figure()
        fig.add_annotation(text=f"Chart failed:<br>{str(e)[:100]}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="red"))
        fig.update_layout(title=f"{title} (Error)", height=400)
        return fig

def generate_fallback_suggestions(df, numeric_cols, categorical_cols, user_prompt):
    """Generate diverse fallback suggestions"""
    suggestions = []
    
    if numeric_cols:
        suggestions.append({"type": "metric_card", "metric_type": "count", "column": None, "title": "Total Records", "description": "Total rows"})
        for col in numeric_cols[:2]:
            suggestions.append({"type": "metric_card", "metric_type": "sum", "column": col, "title": f"Total {col}", "description": f"Sum of {col}"})
            suggestions.append({"type": "metric_card", "metric_type": "avg", "column": col, "title": f"Average {col}", "description": f"Mean of {col}"})
    
    if numeric_cols:
        suggestions.append({"type": "histogram", "x_column": numeric_cols[0], "y_column": None, "color_scheme": "viridis", "title": f"Distribution of {numeric_cols[0]}", "description": "Frequency distribution"})
    
    if len(numeric_cols) >= 2:
        suggestions.append({"type": "scatter", "x_column": numeric_cols[0], "y_column": numeric_cols[1], "color_scheme": "blues", "title": f"{numeric_cols[0]} vs {numeric_cols[1]}", "description": "Relationship"})
    
    if categorical_cols:
        suggestions.append({"type": "bar", "x_column": categorical_cols[0], "y_column": None, "color_scheme": "rainbow", "title": f"Count by {categorical_cols[0]}", "description": "Category breakdown"})
    
    if len(numeric_cols) >= 3:
        suggestions.append({"type": "heatmap", "x_column": None, "y_column": None, "color_scheme": "plasma", "title": "Correlation Matrix", "description": "Correlations"})
    
    return suggestions