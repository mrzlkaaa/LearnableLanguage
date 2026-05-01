#!/usr/bin/env python3
"""
LangGraph MCP Server
Provides workflow orchestration tools via MCP protocol (stdio)

Architecture (interrupt-based):
1. start_workflow → planner runs → interrupt (waiting for external spawn)
2. get_status → check if workflow is interrupted
3. External: sessions_spawn fullstack agent → agent works → agent_callback
4. resume_workflow → fullstack runs → interrupt or callback → complete

Tools:
- langgraph__start_workflow(task, thread_id?) → thread_id (interrupted state)
- langgraph__get_status(thread_id) → current state
- langgraph__list_tasks() → all tasks
- langgraph__resume_workflow(thread_id) → resume interrupted workflow
- langgraph__cancel_workflow(thread_id) → cancel workflow
- langgraph__agent_callback(thread_id, status, result, error?) → update from agent
"""

import json
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import threading
import concurrent.futures

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.runner import get_runner

QUEUE_DIR = Path.home() / ".openclaw" / "tasks"
QUEUE_FILE = QUEUE_DIR / "queue.json"
QUEUE_LOCK = threading.Lock()

PROJECT_PATH = "/home/mrzlka/IT_projects/language_service"

# Thread pool for async graph operations
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# In-memory state store for dynamic plan injection
# This allows external code to update state before resume
_state_store: Dict[str, Dict[str, Any]] = {}


def get_stored_state(thread_id: str) -> Optional[Dict[str, Any]]:
    """Get stored state updates for a thread."""
    return _state_store.get(thread_id)


def store_state(thread_id: str, updates: Dict[str, Any]) -> None:
    """Store state updates for a thread (dynamic plan injection)."""
    if thread_id not in _state_store:
        _state_store[thread_id] = {}
    _state_store[thread_id].update(updates)


def clear_stored_state(thread_id: str) -> None:
    """Clear stored state for a thread."""
    _state_store.pop(thread_id, None)


def load_queue() -> Dict[str, Any]:
    """Load task queue from disk"""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"tasks": [], "count": 0}


def save_queue(queue: Dict[str, Any]) -> None:
    """Save task queue to disk"""
    with QUEUE_LOCK:
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2)


def generate_id(prefix: str = "wf") -> str:
    """Generate unique task ID"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{timestamp}"


class MCP_SERVER:
    def __init__(self):
        self.runner = get_runner()
        self.tools = {
            "start_workflow": self.start_workflow,
            "get_status": self.get_status,
            "list_tasks": self.list_tasks,
            "update_state": self.update_state,
            "resume_workflow": self.resume_workflow,
            "cancel_workflow": self.cancel_workflow,
            "agent_callback": self.agent_callback,
        }
    
    def _read_request(self) -> Optional[Dict[str, Any]]:
        """Read JSON-RPC request from stdin"""
        try:
            line = sys.stdin.readline()
            if not line:
                return None
            return json.loads(line.strip())
        except (json.JSONDecodeError, EOFError):
            return None
    
    def _send_response(self, response: Dict[str, Any]) -> None:
        """Send JSON-RPC response to stdout"""
        print(json.dumps(response), flush=True)
    
    def _send_result(self, id: Any, result: Any) -> None:
        self._send_response({
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        })
    
    def _send_error(self, id: Any, code: int, message: str) -> None:
        self._send_response({
            "jsonrpc": "2.0",
            "id": id,
            "error": {"code": code, "message": message}
        })

    def handle_request(self, request: Dict[str, Any]) -> None:
        """Handle incoming JSON-RPC request"""
        method = request.get("method", "")
        id = request.get("id")
        params = request.get("params", {})
        
        if method == "initialize":
            self._send_result(id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "langgraph", "version": "1.0.0"}
            })
        elif method == "tools/list":
            tools_list = [
                {
                    "name": "start_workflow",
                    "description": "Start a new workflow task. Returns thread_id and runs planner node only (interrupts for external spawn)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string"},
                            "thread_id": {"type": "string"}
                        },
                        "required": ["task"]
                    }
                },
                {
                    "name": "get_status",
                    "description": "Get current workflow status from checkpointer",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"thread_id": {"type": "string"}},
                        "required": ["thread_id"]
                    }
                },
                {
                    "name": "list_tasks",
                    "description": "List all tasks from queue",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "update_state",
                    "description": "Dynamically inject/update state for a workflow thread. Allows plan injection for multi-step tasks.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string"},
                            "plan": {"type": "array", "items": {"type": "string"}},
                            "current_step": {"type": "integer"},
                            "status": {"type": "string"},
                            "task": {"type": "string"}
                        },
                        "required": ["thread_id"]
                    }
                },
                {
                    "name": "resume_workflow",
                    "description": "Resume an interrupted workflow from checkpoint. Runs fullstack node.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"thread_id": {"type": "string"}},
                        "required": ["thread_id"]
                    }
                },
                {
                    "name": "cancel_workflow",
                    "description": "Cancel a queued or running workflow",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["thread_id"]
                    }
                },
                {
                    "name": "agent_callback",
                    "description": "Agent reports completion/failure. Updates queue and can trigger resume.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string"},
                            "status": {"type": "string"},
                            "result": {"type": "string"},
                            "error": {"type": "string"}
                        },
                        "required": ["thread_id", "status"]
                    }
                },
            ]
            self._send_result(id, {"tools": tools_list})
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](tool_args)
                    self._send_result(id, {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self._send_error(id, -32603, f"Tool error: {str(e)}")
            else:
                self._send_error(id, -32601, f"Unknown tool: {tool_name}")
        else:
            if id:
                self._send_error(id, -32601, f"Unknown method: {method}")
    
    # Tool implementations
    
    def start_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start workflow: runs planner node only, then interrupts.
        
        Returns:
            thread_id, status='interrupted', plan from planner
        """
        task = args.get("task", "")
        thread_id = args.get("thread_id") or generate_id("wf")
        
        # Create queue entry
        queue = load_queue()
        task_entry = {
            "thread_id": thread_id,
            "task": task,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        queue["tasks"].append(task_entry)
        queue["count"] = len(queue["tasks"])
        save_queue(queue)
        
        # Run initial invoke (planner only, stops at interrupt)
        try:
            result = asyncio.run(self.runner.start(thread_id, task, PROJECT_PATH))
            
            # Store initial state for later update_state access
            store_state(thread_id, {
                "task": task,
                "plan": result.get("plan", []),
                "current_step": result.get("current_step", 0),
                "status": "interrupted",
                "project_path": PROJECT_PATH
            })
            
            # Update queue with current state
            queue = load_queue()
            for t in queue["tasks"]:
                if t["thread_id"] == thread_id:
                    t["status"] = "interrupted"  # Waiting for external spawn
                    t["updated_at"] = datetime.now().isoformat()
                    t["plan"] = result.get("plan", [])
                    t["current_step"] = result.get("current_step", 0)
                    break
            save_queue(queue)
            
            return {
                "thread_id": thread_id,
                "status": "interrupted",
                "plan": result.get("plan", []),
                "current_step": result.get("current_step", 0),
                "message": "Planner completed. Use update_state to inject custom plan, then resume_workflow."
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"thread_id": thread_id, "status": "failed", "error": str(e)}
    
    def get_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current workflow state from checkpointer."""
        thread_id = args.get("thread_id", "")
        
        state = self.runner.get_state(thread_id)
        
        if state:
            status = state.get("status", "unknown")
            # If waiting at interrupt point, show as interrupted
            if status == "pending" and state.get("current_step", 0) > 0:
                status = "interrupted"
            
            return {
                "thread_id": thread_id,
                "status": status,
                "task": state.get("task", ""),
                "plan": state.get("plan", []),
                "current_step": state.get("current_step", 0),
                "result": state.get("result"),
                "error": state.get("error"),
            }
        
        # Fallback to queue
        queue = load_queue()
        for task in queue["tasks"]:
            if task["thread_id"] == thread_id:
                return task
        
        return {"error": "Task not found", "thread_id": thread_id}
    
    def list_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all tasks from queue."""
        queue = load_queue()
        return {"tasks": queue.get("tasks", []), "count": queue.get("count", 0)}
    
    def update_state(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically inject/update state for a workflow thread.
        
        This enables graph-based plan injection:
        - External planner can update plan before resume_workflow
        - Can update current_step, plan, status, task, etc.
        
        Usage:
        1. start_workflow → get thread_id
        2. update_state(thread_id, plan=[...]) → inject custom plan
        3. resume_workflow → graph uses injected plan
        """
        thread_id = args.get("thread_id", "")
        
        if not thread_id:
            return {"error": "thread_id is required"}
        
        # Extract updateable fields
        updates = {}
        if "plan" in args:
            updates["plan"] = args["plan"]
        if "current_step" in args:
            updates["current_step"] = args["current_step"]
        if "status" in args:
            updates["status"] = args["status"]
        if "task" in args:
            updates["task"] = args["task"]
        
        # Get current state
        current_state = self.runner.get_state(thread_id)
        if not current_state:
            # Try to get from checkpointer via resume to init state
            return {"error": f"Thread {thread_id} not found. Call start_workflow first."}
        
        # Update checkpointer state
        config = {"configurable": {"thread_id": thread_id}}
        self.runner.graph.update_state(config, updates)
        
        # Also store in memory for reference
        store_state(thread_id, updates)
        
        return {
            "thread_id": thread_id,
            "status": "updated",
            "updated_fields": list(updates.keys()),
            "message": f"State updated. Call resume_workflow to continue with new state."
        }
    
    def resume_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resume interrupted workflow.
        
        Runs fullstack node for current step, then:
        - If more steps → interrupts again
        - If done → callback node → completed
        
        Returns:
            Final state or interrupted state with next step info
        """
        thread_id = args.get("thread_id", "")
        
        try:
            result = self.runner.resume_workflow(thread_id)
            
            # Update queue
            queue = load_queue()
            for t in queue["tasks"]:
                if t["thread_id"] == thread_id:
                    t["status"] = result.get("status", "unknown")
                    t["updated_at"] = datetime.now().isoformat()
                    t["result"] = result
                    t["current_step"] = result.get("current_step", 0)
                    break
            save_queue(queue)
            
            return {
                "thread_id": thread_id,
                "status": result.get("status", "unknown"),
                "current_step": result.get("current_step", 0),
                "result": result.get("result"),
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e), "thread_id": thread_id}
    
    def cancel_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a workflow."""
        thread_id = args.get("thread_id", "")
        reason = args.get("reason", "Cancelled by user")
        
        try:
            self.runner.cancel(thread_id)
        except Exception:
            pass
        
        queue = load_queue()
        for task in queue["tasks"]:
            if task["thread_id"] == thread_id:
                task["status"] = "cancelled"
                task["updated_at"] = datetime.now().isoformat()
                task["cancelled_reason"] = reason
                task["cancelled_at"] = datetime.now().isoformat()
                save_queue(queue)
                return {
                    "thread_id": thread_id,
                    "status": "cancelled",
                    "reason": reason,
                    "cancelled_at": task["cancelled_at"]
                }
        
        return {"error": "Task not found", "thread_id": thread_id}
    
    def agent_callback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent reports completion. Used by external fullstack agents.
        
        Updates queue but does NOT auto-resume (planner agent should call resume_workflow).
        """
        thread_id = args.get("thread_id", "")
        status = args.get("status", "completed")
        result = args.get("result", "")
        error = args.get("error")
        
        queue = load_queue()
        
        for task in queue["tasks"]:
            if task["thread_id"] == thread_id:
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                if result:
                    try:
                        task["result"] = json.loads(result)
                    except:
                        task["result"] = result
                if error:
                    task["error"] = error
                break
        else:
            queue["tasks"].append({
                "thread_id": thread_id,
                "status": status,
                "result": result,
                "error": error,
                "updated_at": datetime.now().isoformat(),
            })
        
        save_queue(queue)
        return {"thread_id": thread_id, "status": status, "updated_at": datetime.now().isoformat()}


def main():
    server = MCP_SERVER()
    
    # Send initial handshake
    print(json.dumps({"jsonrpc": "2.0", "method": "initialized", "params": {}}), flush=True)
    
    while True:
        request = server._read_request()
        if request is None:
            break
        server.handle_request(request)


if __name__ == "__main__":
    main()