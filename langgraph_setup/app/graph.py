"""LangGraph workflow definition."""
from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.nodes.planner import plan_task
from app.nodes.fullstack import execute_task
from app.nodes.callback import finalize


def should_continue(state: AgentState) -> str:
    """Determine next node based on current step vs plan length.
    
    Returns:
        "fullstack" to execute next step, "callback" to finalize
    """
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])
    
    if current_step >= len(plan):
        # All steps done - go to callback
        return "callback"
    else:
        # More steps to execute - go to fullstack
        return "fullstack"


def create_graph(checkpointer=None):
    """Create and compile the StateGraph workflow.
    
    Architecture:
        START → planner → [interrupt] → fullstack → [conditional loop] → callback → END
                               ↑                                           |
                               └───────────────────────────────────────────┘
                                         (if more steps remain)
    
    How it works:
    1. START → planner: decomposes task into steps
    2. planner → [interrupt]: pauses before execution (allows external inspection)
    3. [interrupt] → fullstack: executes current step
    4. fullstack → [should_continue]: checks if more steps remain
       - If more steps: loop back to [interrupt] before fullstack (exposes state for inspection)
       - If no more steps: go to callback
    5. callback: finalize (update docs, report result)
    6. callback → END: workflow complete
    
    Args:
        checkpointer: Optional checkpointer for state persistence
    
    Returns:
        Compiled StateGraph ready for execution
    """
    graph = StateGraph(AgentState)
    
    # Add nodes - all sync functions
    graph.add_node("planner", plan_task)
    graph.add_node("fullstack", execute_task)
    graph.add_node("callback", finalize)
    
    # Flow definition:
    # 1. START → planner
    graph.add_edge(START, "planner")
    
    # 2. After planner, decide: fullstack or callback
    graph.add_conditional_edges(
        "planner",
        should_continue,
        {
            "fullstack": "fullstack",  # First step - execute
            "callback": "callback"      # No steps needed
        }
    )
    
    # 3. After fullstack, decide: continue with next step or finalize
    graph.add_conditional_edges(
        "fullstack",
        should_continue,
        {
            "fullstack": "fullstack",  # More steps - loop back (hits interrupt)
            "callback": "callback"      # All done
        }
    )
    
    # 4. callback → END
    graph.add_edge("callback", END)
    
    # Compile with interrupt BEFORE fullstack
    # This allows external inspection/modification between steps
    return graph.compile(
        checkpointer=checkpointer, 
        interrupt_before=["fullstack"]
    )