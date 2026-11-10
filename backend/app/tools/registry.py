"""Tool registry with decorator-based registration."""
from typing import Any, Callable, Dict, Optional


class ToolRegistry:
    """Central registry for all AI-callable tools."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        self._tools[name] = func

    def get(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._tools


# Global singleton registry
registry = ToolRegistry()


def register_tool(name: Optional[str] = None):
    """Decorator to register a function as a named tool."""
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        registry.register(tool_name, func)
        return func
    return decorator
