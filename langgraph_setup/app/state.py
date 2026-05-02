from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # chat history
    task: str                                 # current task description
    plan: list[str]                            # decomposed steps
    current_step: int                         # which step we're on
    result: Optional[dict]                     # execution result
    status: str                               # "working" | "completed" | "failed" | "cancelled"
    thread_id: str                            # workflow thread ID
    project_path: str                         # /home/mrzlka/IT_projects/language_service
    error: Optional[str]                       # error message if failed