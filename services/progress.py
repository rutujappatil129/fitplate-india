from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import pandas as pd

def compute_weight_analytics(logs: List[Any], target_weight_kg: float) -> Dict[str, Any]:
    """Calculates statistics: start weight, current weight, delta, and distance to target."""
    if not logs:
        return {
            "has_data": False,
            "start_weight": 0.0,
            "current_weight": 0.0,
            "weight_change": 0.0,
            "distance_to_target": 0.0,
            "target_weight": target_weight_kg,
            "message": "No weight logs recorded yet. Add your first entry to track your trend!"
        }
    
    sorted_logs = sorted(logs, key=lambda x: (x["log_date"], x["id"]))
    start_wt = float(sorted_logs[0]["weight_kg"])
    curr_wt = float(sorted_logs[-1]["weight_kg"])
    change = round(curr_wt - start_wt, 1)
    dist = round(curr_wt - target_weight_kg, 1)
    
    return {
        "has_data": True,
        "start_weight": start_wt,
        "current_weight": curr_wt,
        "weight_change": change,
        "distance_to_target": dist,
        "target_weight": target_weight_kg,
        "entries_count": len(sorted_logs),
        "message": (
            f"You have logged {len(sorted_logs)} entries. Total change: {change:+} kg."
        )
    }

def create_weight_trend_chart(logs: List[Any], target_weight_kg: float) -> go.Figure:
    """Builds an interactive Plotly weight trend chart with target milestone line."""
    fig = go.Figure()
    
    if not logs:
        fig.add_annotation(
            text="No weight records yet. Use 'Log Today's Weight' above to start tracking!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#6b7280")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=320,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        return fig

    sorted_logs = sorted(logs, key=lambda x: (x["log_date"], x["id"]))
    dates = [row["log_date"] for row in sorted_logs]
    weights = [float(row["weight_kg"]) for row in sorted_logs]
    
    # 1. Actual weight series
    fig.add_trace(go.Scatter(
        x=dates,
        y=weights,
        mode="lines+markers",
        name="Recorded Weight (kg)",
        line=dict(color="#10b981", width=3),
        marker=dict(size=8, color="#047857", symbol="circle"),
        hovertemplate="<b>Date:</b> %{x}<br><b>Weight:</b> %{y} kg<extra></extra>"
    ))

    # 2. Target weight benchmark
    fig.add_trace(go.Scatter(
        x=[dates[0], dates[-1]],
        y=[target_weight_kg, target_weight_kg],
        mode="lines",
        name="Target Goal",
        line=dict(color="#f59e0b", width=2, dash="dash"),
        hovertemplate="<b>Target:</b> %{y} kg<extra></extra>"
    ))

    fig.update_layout(
        title="Weight Progress Over Time (kg)",
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig
