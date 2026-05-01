from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # chat history
    task: str                                 # current task description
    plan: list[str]                            # decomposed steps
    current_step: int                         # which step we're on
    result: Optional[dict]                     # execution result
    status: str                               # "working" | "completed" | "failed" | "cancelled" | "waiting_for_callback" | "needs_review"
    thread_id: str                            # workflow thread ID
    project_path: str                         # /home/mrzlka/IT_projects/language_service
    error: Optional[str]                       # error message if failed
    relevant_files: Optional[list[str]]        # files relevant to current step
    code_review: Optional[dict]                 # code review result from planner
    review_context: Optional[dict]             # context for code review (from prepare_review node)