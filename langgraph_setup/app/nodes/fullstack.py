"""Fullstack node - spawns and monitors fullstack agent execution.

Persistent Session Flow:
- Node writes task file for current step (WITHOUT incrementing step)
- Sets status="waiting_for_callback" to signal external spawn
- External code spawns agent in PERSISTENT session via sessions_spawn(mode="session")
- Agent works → calls langgraph__agent_callback
- External code: update_state(current_step +1) → resume_workflow
- Node sees incremented step → writes next task, returns without incrementing
- Repeat until all steps done

This enables 1 project = 1 persistent fullstack session.

Flow:
1. start_workflow → planner → interrupt
2. resume_workflow → fullstack node writes task, status="waiting_for_callback" → interrupt
3. External: sessions_spawn(mode="session") to create persistent session ONCE
4. External: sessions_send to that session with task info
5. Agent works → agent_callback
6. External: update_state(current_step+1) → resume_workflow
7. fullstack node: sees step changed → writes next task, returns
8. External: sessions_send(next task) to same persistent session
9. Repeat 5-8 until done
10. When callback reports done → callback node → END
"""
import json
import os
from datetime import datetime
from app.state import AgentState


def get_verified_bugs(project_path: str) -> str:
    """Get list of verified bugs from .bugs_fixed.json.
    
    This replaces hardcoded bugs_fixed_text with machine-readable data.
    If .bugs_fixed.json doesn't exist yet, falls back to empty string
    (first run will seed the database).
    """
    bugs_db_path = os.path.join(project_path, ".bugs_fixed.json")
    
    if not os.path.exists(bugs_db_path):
        return ""  # No database yet, first run
    
    try:
        with open(bugs_db_path, 'r') as f:
            bugs_db = json.load(f)
        
        verified_bugs = []
        if "bugs_fixed" in bugs_db:
            for entry in bugs_db["bugs_fixed"]:
                if entry.get("verified", False):
                    bug = entry.get("bug", "")
                    if bug:
                        verified_bugs.append(f"- {bug}")
        
        if verified_bugs:
            return "УЖЕ ИСПРАВЛЕНО (НЕ искать как баги):\n" + "\n".join(verified_bugs)
        return ""
    except Exception:
        return ""


def read_project_files(project_path: str, step_name: str) -> dict:
    """Read relevant project files to provide context for the agent.
    
    Reads key files based on step_name to give agent full context
    about existing code structure.
    
    Returns dict with:
        - relevant_files: list of file paths that were read
        - files_content: dict mapping path -> content (truncated to 150 lines)
    """
    relevant_files = []
    files_content = {}
    
    # Map step keywords to relevant files
    step_lower = step_name.lower()
    
    # Backend/API steps
    if any(k in step_lower for k in ["backend", "api", "database", "service", "repo"]):
        backend_files = [
            "backend/main.py",
            "backend/app/core/services/notifications.py",
            "backend/app/core/services/words_supply.py",
            "backend/app/core/services/words_learning.py",
            "backend/app/core/services/broadcaster.py",
            "backend/app/database/repo/vocabulary.py",
        ]
        for f in backend_files:
            fpath = os.path.join(project_path, f)
            if os.path.exists(fpath):
                relevant_files.append(f)
    
    # Frontend/UI steps
    if any(k in step_lower for k in ["frontend", "ui", "telegram", "handler", "keyboard"]):
        frontend_files = [
            "backend/app/handlers/user/words_learning.py",
            "backend/app/handlers/user/onboarding.py",
            "backend/app/handlers/general.py",
            "backend/app/keyboards/for_notifications.py",
            "backend/app/keyboards/learning/for_words.py",
        ]
        for f in frontend_files:
            fpath = os.path.join(project_path, f)
            if os.path.exists(fpath):
                relevant_files.append(f)
    
    # Review step - read changed files from previous result
    if "review" in step_lower:
        # Check for result files that might contain file list
        task_dir = os.path.expanduser("~/.openclaw/tasks/")
        if os.path.exists(task_dir):
            for fname in os.listdir(task_dir):
                if fname.endswith(".task"):
                    try:
                        with open(os.path.join(task_dir, fname), 'r') as f:
                            task_data = json.load(f)
                            prev_files = task_data.get("result", {}).get("files_changed", [])
                            for pf in prev_files:
                                if pf not in relevant_files:
                                    relevant_files.append(pf)
                    except:
                        pass
    
    # Default files - always include for context
    default_files = [
        "backend/main.py",
        "backend/app/config.py",
    ]
    for f in default_files:
        fpath = os.path.join(project_path, f)
        if os.path.exists(fpath) and f not in relevant_files:
            relevant_files.append(f)
    
    # Read file contents (max 150 lines each)
    for f in relevant_files:
        fpath = os.path.join(project_path, f)
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r') as fh:
                    lines = fh.readlines()
                    if len(lines) > 150:
                        content = ''.join(lines[:150]) + f"\n... [truncated, {len(lines) - 150} more lines]"
                    else:
                        content = ''.join(lines)
                    files_content[f] = content
            except Exception as e:
                files_content[f] = f"[Error reading: {str(e)}]"
    
    return {
        "relevant_files": relevant_files,
        "files_content": files_content
    }


def build_task_context(state: AgentState) -> str:
    """Build comprehensive task context for the fullstack agent.
    
    Includes:
    - Task description
    - Verified bugs (from .bugs_fixed.json)
    - Relevant project files with content
    - Current step info
    - Plan info
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    task = state.get("task", "")
    thread_id = state.get("thread_id", "")
    project_path = state.get("project_path", "")
    
    step = plan[current_step] if current_step < len(plan) else "unknown"
    total_steps = len(plan)
    
    # Get verified bugs
    verified_bugs = get_verified_bugs(project_path)
    if not verified_bugs:
        verified_bugs = "УЖЕ ИСПРАВЛЕНО:\n- (первый запуск,暂无数据)"
    
    # Read relevant project files
    file_info = read_project_files(project_path, step)
    relevant_files = file_info["relevant_files"]
    files_content = file_info["files_content"]
    
    # Build files section
    files_section = ""
    if files_content:
        files_section = "\n\n=== РЕЛЕВАНТНЫЕ ФАЙЛЫ ПРОЕКТА ===\n\n"
        for fname, content in files_content.items():
            files_section += f"\n--- {fname} ---\n{content}\n"
    
    task_for_agent = f"""=== ЗАДАНИЕ ===
{task}

=== УЖЕ ИСПРАВЛЕННЫЕ БАГИ (НЕ трогать) ===
{verified_bugs}

=== ТЕКУЩИЙ ШАГ ===
Step {current_step + 1}/{total_steps}: {step}

=== ПРОЕКТ ПУТЬ ===
{project_path}

{files_section}

=== ПРОТОКОЛ ЗАВЕРШЕНИЯ ===
После выполнения ВЫЗОВИ langgraph__agent_callback:
- status: "completed" или "failed"
- result: JSON с:
  {{
    "files_changed": ["список файлов которые изменил"],
    "bugs_fixed": ["список исправленных багов"],
    "new_features": ["что добавлено"],
    "status": "что изменилось в проекте",
    "next_steps": ["рекомендуемые следующие шаги"]
  }}
  
Также ОБЯЗАТЕЛЬНО обнови state.json в корне проекта:
- tasks.backend.status = "done" или актуальный
- tasks.backend.updated_at = текущая дата

=== РЕЛЕВАНТНЫЕ ФАЙЛЫ (прочитай их) ===
{', '.join(relevant_files) if relevant_files else '(none)'}
"""
    
    return task_for_agent, relevant_files


def execute_task(state: AgentState) -> AgentState:
    """Coordinates fullstack execution for current step.
    
    Key difference from one-shot model:
    - Does NOT increment current_step (external code does this after callback)
    - Sets status="waiting_for_callback" to signal "spawn agent now"
    - Writes task file with EXACTLY the current step (not step+1)
    - Reads verified bugs from .bugs_fixed.json (not hardcoded)
    
    This enables persistent session model:
    1. Node writes task for current step, returns (interrupt)
    2. External spawns agent (persistent session)
    3. Agent works → callback
    4. External increments step → resume
    5. Node writes task for next step (or completes)
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
        state["messages"] = state.get("messages", []) + ["All steps completed - ready for callback node"]
        return state
    
    # Get current step info
    step = plan[current_step]
    total_steps = len(plan)
    
    # Update status - signal that agent needs to be spawned
    state["status"] = "waiting_for_callback"
    state["messages"] = state.get("messages", []) + [
        f"Step {current_step + 1}/{total_steps}: {step} - ready for spawn"
    ]
    
    # Build the task description for fullstack
    # Read verified bugs from .bugs_fixed.json (machine-readable, not hardcoded)
    verified_bugs = get_verified_bugs(project_path)
    
    # Fallback to minimal static list only if no .bugs_fixed.json exists yet
    if not verified_bugs:
        # This is a FIRST RUN scenario - minimal context
        verified_bugs = "УЖЕ ИСПРАВЛЕНО:\n- (первый запуск,暂无 данных)"
    
    # Build task context with project files
    task_for_agent, relevant_files = build_task_context(state)
    
    # Write task to file for external session to pick up
    task_file = os.path.expanduser(f"~/.openclaw/tasks/{thread_id}.task")
    os.makedirs(os.path.dirname(task_file), exist_ok=True)
    
    with open(task_file, 'w') as f:
        json.dump({
            "task": task_for_agent,
            "step": current_step,
            "total_steps": total_steps,
            "step_name": step,
            "status": "ready_for_spawn",
            "thread_id": thread_id,
            "created_at": datetime.now().isoformat(),
            "verified_bugs_source": ".bugs_fixed.json" if os.path.exists(os.path.join(project_path, ".bugs_fixed.json")) else "none",
            "relevant_files": relevant_files,
            "project_path": project_path
        }, f, indent=2)
    
    # DO NOT increment current_step here!
    # External code will increment via update_state after agent_callback
    # This is the key difference from one-shot model
    
    # Log what we did
    state["relevant_files"] = relevant_files
    state["messages"] = state.get("messages", []) + [
        f"Task file written: {task_file}",
        f"Relevant files for context: {len(relevant_files)}",
        f"Waiting for external agent to spawn and complete step {current_step + 1}"
    ]
    
    return state


def update_step_result(state: AgentState, result: dict) -> AgentState:
    """Update state with step execution result.
    
    Called by external code after agent_callback to record what happened.
    Note: step increment happens via update_state, not here.
    """
    state["result"] = result
    
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    
    if current_step >= len(plan):
        state["status"] = "completed"
        state["messages"] = state.get("messages", []) + ["All steps completed successfully"]
    else:
        state["messages"] = state.get("messages", []) + [f"Step {current_step} complete"]
    
    return state


def set_error(state: AgentState, error: str) -> AgentState:
    """Mark step as failed."""
    state["status"] = "failed"
    state["error"] = error
    state["messages"] = state.get("messages", []) + [f"Error: {error}"]
    return state


def check_step_done(state: AgentState) -> AgentState:
    """Check if current step is marked as done in task file."""
    thread_id = state.get("thread_id", "")
    task_file = os.path.expanduser(f"~/.openclaw/tasks/{thread_id}.task")
    
    if os.path.exists(task_file):
        try:
            with open(task_file, 'r') as f:
                task_info = json.load(f)
            
            if task_info.get("status") == "completed":
                # Agent finished this step - ready for next
                state["messages"] = state.get("messages", []) + [
                    f"Step {task_info.get('step', 0) + 1} marked as completed by agent"
                ]
        except Exception:
            pass
    
    return state