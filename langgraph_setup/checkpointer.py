"""Checkpointer setup using memory or SQLite."""
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer(db_path: str = None) -> MemorySaver:
    """Create a checkpointer.
    
    Args:
        db_path: Ignored (kept for compatibility). Use MemorySaver in-memory.
                For production with persistence, install langgraph[all] or
                use a custom SqliteSaver from langgraph.checkpoint.sqlite.
    
    Returns:
        MemorySaver instance for the workflow
    """
    return MemorySaver()