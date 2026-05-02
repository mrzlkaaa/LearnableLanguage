"""Workflow runner with async streaming support."""
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from app.state import AgentState
from app.graph import create_graph
from checkpointer import get_checkpointer


class WorkflowRunner:
    """Manages LangGraph workflow execution with streaming."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.checkpointer = get_checkpointer(db_path)
        self.graph = create_graph(checkpointer=self.checkpointer)
    
    async def start(self, thread_id: str, task: str, project_path: str) -> Dict[str, Any]:
        """Start workflow: runs planner only (interrupt pattern)."""
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = AgentState(
            messages=[],
            task=task,
            plan=[],
            current_step=0,
            result=None,
            status="pending",
            thread_id=thread_id,
            project_path=project_path,
            error=None
        )
        return await self.graph.ainvoke(initial_state, config)

    async def resume_workflow(self, thread_id: str) -> Dict[str, Any]:
        """Resume from interrupt: runs fullstack for current step."""
        config = {"configurable": {"thread_id": thread_id}}
        return await self.graph.ainvoke(None, config)

    def cancel(self, thread_id: str) -> bool:
        """Cancel running workflow."""
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(config, {"status": "cancelled"})
        return True

    # Legacy aliases for backwards compatibility
    async def run_workflow(
        self,
        thread_id: str,
        task: str,
        project_path: str
    ) -> Dict[str, Any]:
        """Run the workflow synchronously to completion."""
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = AgentState(
            messages=[],
            task=task,
            plan=[],
            current_step=0,
            result=None,
            status="pending",
            thread_id=thread_id,
            project_path=project_path,
            error=None
        )
        return await self.graph.ainvoke(initial_state, config)
    
    async def stream_workflow(
        self,
        thread_id: str,
        task: str,
        project_path: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream workflow events as they occur."""
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = AgentState(
            messages=[],
            task=task,
            plan=[],
            current_step=0,
            result=None,
            status="pending",
            thread_id=thread_id,
            project_path=project_path,
            error=None
        )
        async for event in self.graph.astream_events(initial_state, config):
            yield {
                "node": event.get("name"),
                "event": event.get("event"),
                "data": event.get("data")
            }
    
    def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow state."""
        config = {"configurable": {"thread_id": thread_id}}
        try:
            state = self.graph.get_state(config)
            return state.values if state else None
        except Exception:
            return None
    
    def interrupt(self, thread_id: str) -> bool:
        """Interrupt a running workflow."""
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(config, {"status": "cancelled"})
        return True
    
    async def resume(self, thread_id: str) -> Dict[str, Any]:
        """Resume an interrupted workflow."""
        return await self.resume_workflow(thread_id)


_runner: Optional[WorkflowRunner] = None


def get_runner() -> WorkflowRunner:
    """Get or create the global workflow runner."""
    global _runner
    if _runner is None:
        _runner = WorkflowRunner()
    return _runner