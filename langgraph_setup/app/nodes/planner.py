"""Planner node - decomposes task into steps.

Dynamic plan injection:
- If state["plan"] is already provided (injected externally), use it as-is
- This enables external code (via update_state or initial state) to control the plan
- Only generates default steps if plan is empty
"""
from app.state import AgentState


def plan_task(state: AgentState) -> AgentState:
    """Analyzes task and creates execution plan.
    
    Supports dynamic plan injection:
    - If state["plan"] already contains steps (injected externally), use those
    - Only auto-generate if plan is empty or not provided
    
    This allows the planner agent to inject custom plans via update_state
    before or after this node runs.
    """
    existing_plan = state.get("plan", [])
    
    # If plan was already injected (dynamic state), use it
    if existing_plan and len(existing_plan) > 0:
        state["current_step"] = 0
        state["messages"] = state.get("messages", []) + [f"Using injected plan with {len(existing_plan)} steps: {', '.join(existing_plan)}"]
        return state
    
    # Otherwise, use built-in keyword-based planner (fallback)
    task = state.get("task", "")
    steps = []
    task_lower = task.lower()
    
    if "backend" in task_lower or "api" in task_lower or "database" in task_lower:
        steps.append("Analyze backend requirements")
        steps.append("Implement backend components")
        steps.append("Add tests and validation")
    
    if "frontend" in task_lower or "ui" in task_lower or "react" in task_lower:
        steps.append("Design frontend architecture")
        steps.append("Implement UI components")
        steps.append("Integrate with backend API")
    
    if "auth" in task_lower or "login" in task_lower or "jwt" in task_lower:
        steps.append("Implement authentication system")
    
    if "database" in task_lower or "schema" in task_lower:
        steps.append("Design database schema")
        steps.append("Implement data models")
    
    if not steps:
        steps = [
            "Analyze requirements",
            "Implement solution",
            "Test and validate",
            "Update documentation"
        ]
    
    state["plan"] = steps
    state["current_step"] = 0
    state["messages"] = state.get("messages", []) + [f"Task decomposed into {len(steps)} steps: {', '.join(steps)}"]
    
    return state