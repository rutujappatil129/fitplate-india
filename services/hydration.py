from typing import Dict, Any

def get_hydration_progress(consumed_ml: int, target_ml: int) -> Dict[str, Any]:
    """Computes hydration statistics, remaining volume, and completion percentage."""
    target = max(target_ml, 1000)
    consumed = max(consumed_ml, 0)
    pct = min(round((consumed / target) * 100, 1), 100.0)
    remaining = max(target - consumed, 0)
    
    return {
        "consumed_ml": consumed,
        "target_ml": target,
        "percentage": pct,
        "remaining_ml": remaining,
        "is_target_met": consumed >= target,
        "status_message": (
            "Goal achieved! Excellent hydration today." if consumed >= target
            else f"Keep sipping! {remaining} ml remaining to reach your daily goal."
        )
    }
