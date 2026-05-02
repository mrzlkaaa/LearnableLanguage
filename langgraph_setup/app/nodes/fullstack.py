"""Fullstack node - spawns and monitors fullstack agent execution.

Dynamic flow support:
- This node coordinates state for external sessions_spawn integration
- Actual spawning happens outside the graph (via external code)
- Step progression is controlled by external resume_workflow calls

Flow:
1. External code: start_workflow → interrupt
2. External code: update_state with plan (dynamic injection)
3. External code: sessions_spawn with current step task
4. External code: resume_workflow → this node runs → interrupt
5. Repeat steps 3-4 for each step
6. When current_step >= len(plan) → callback node
"""
import json
import os
from app.state import AgentState


def execute_task(state: AgentState) -> AgentState:
    """Coordinates fullstack execution for current step.
    
    This node:
    1. Reads current step from plan
    2. Writes task info to file (for external spawning reference)
    3. Updates state with execution status
    4. Increments current_step for next iteration
    
    Note: Actual agent spawning happens via external sessions_spawn,
    not inside this node. This node just manages state progression.
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    task = state.get("task", "")
    thread_id = state.get("thread_id", "")
    project_path = state.get("project_path", "")
    
    # Check if all steps are done
    if current_step >= len(plan):
        state["status"] = "completed"
        state["result"] = {"message": "All steps completed"}
        return state
    
    # Get current step
    step = plan[current_step]
    
    # Update status
    state["status"] = "working"
    state["messages"] = state.get("messages", []) + [f"Executing step {current_step + 1}: {step}"]
    
    # Build the task description for fullstack
    # This will be picked up by MCP server for actual spawning
    task_for_agent = f"""Task: {task}

Current step: {current_step + 1}/{len(plan)}
Plan step: {step}

Project path: {project_path}

=== ПРОТОКОЛ ЗАВЕРШЕНИЯ ===
После выполнения ВЫЗОВИ langgraph__agent_callback:
- status: "completed" или "failed"
- result: JSON с:
  {{
    "files_changed": ["список файлов"],
    "bugs_fixed": ["список исправленных багов"],
    "new_features": ["что добавлено"],
    "status": "что изменилось в проекте",
    "next_steps": ["рекомендуемые следующие шаги"]
  }}
  
Также ОБЯЗАТЕЛЬНО обнови state.json в корне проекта:
- tasks.backend.status = "done" или актуальный
- tasks.backend.updated_at = текущая дата
"""
    
    # Write task to a file that MCP server can pick up
    # This is a simple inter-process communication mechanism
    task_file = os.path.expanduser(f"~/.openclaw/tasks/{thread_id}.task")
    os.makedirs(os.path.dirname(task_file), exist_ok=True)
    
    with open(task_file, 'w') as f:
        json.dump({
            "task": task_for_agent,
            "step": current_step,
            "total_steps": len(plan),
            "status": "pending"
        }, f)
    
    # Mark step as in progress - actual spawning happens via MCP
    # The mcp_server reads these task files and spawns agents
    
    # For now, we'll increment the step since this is a demo
    # In production, the callback from the agent would trigger next step
    state["current_step"] = current_step + 1
    
    return state


def update_step_result(state: AgentState, result: dict) -> AgentState:
    """Update state with step execution result."""
    state["result"] = result
    state["current_step"] = state.get("current_step", 0) + 1
    
    # Check if more steps remain
    plan = state.get("plan", [])
    current = state.get("current_step", 0)
    
    if current >= len(plan):
        state["status"] = "completed"
        state["messages"] = state.get("messages", []) + ["All steps completed successfully"]
    else:
        state["messages"] = state.get("messages", []) + [f"Step {current} complete, moving to next step"]
    
    return state


def set_error(state: AgentState, error: str) -> AgentState:
    """Mark step as failed."""
    state["status"] = "failed"
    state["error"] = error
    state["messages"] = state.get("messages", []) + [f"Error: {error}"]
    return state