"""Callback node - finalizes workflow and updates state."""
import json
import os
from datetime import datetime
from app.state import AgentState


def finalize(state: AgentState) -> AgentState:
    """Finalize workflow: update state.json and prepare final report."""
    project_path = state.get("project_path", "")
    thread_id = state.get("thread_id", "")
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])
    error = state.get("error", None)
    
    # Determine final status based on error or completion
    if error:
        final_status = "failed"
    elif current_step >= len(plan):
        final_status = "completed"
    else:
        final_status = "partial"
    
    state["status"] = final_status
    
    # Prepare result summary
    result = {
        "thread_id": thread_id,
        "status": final_status,
        "task": state.get("task", ""),
        "plan": plan,
        "steps_completed": current_step,
        "total_steps": len(plan),
        "error": error
    }
    state["result"] = result
    
    # Update project state.json
    if project_path:
        state_json_path = os.path.join(project_path, "state.json")
        if os.path.exists(state_json_path):
            try:
                with open(state_json_path, "r") as f:
                    project_state = json.load(f)
                
                # Ensure tasks structure exists
                if "tasks" not in project_state:
                    project_state["tasks"] = {}
                
                # Update backend task status
                if "backend" in project_state["tasks"]:
                    project_state["tasks"]["backend"]["status"] = final_status
                    project_state["tasks"]["backend"]["updated_at"] = datetime.now().isoformat()
                
                # Update project status
                project_state["status"] = final_status
                project_state["updated_at"] = datetime.now().isoformat()
                
                # Store result
                project_state["last_result"] = result
                
                with open(state_json_path, "w") as f:
                    json.dump(project_state, f, indent=2)
                
                state["messages"] = state.get("messages", []) + [f"Updated {state_json_path}"]
            except Exception as e:
                state["messages"] = state.get("messages", []) + [f"Failed to update state.json: {str(e)}"]
    
    # Add completion message
    if error:
        state["messages"] = state.get("messages", []) + [f"Workflow failed: {error}"]
    else:
        state["messages"] = state.get("messages", []) + [f"Workflow completed: {current_step}/{len(plan)} steps"]
    
    return state