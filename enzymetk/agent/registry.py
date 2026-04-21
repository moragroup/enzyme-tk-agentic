"""
Tool registry for discovering and retrieving enzyme engineering tools.
"""

from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from enzymetk.agent.tools.base import EnzymeTool


class ToolInfo:
    """Lightweight descriptor for a registered tool."""

    def __init__(self, name: str, description: str, category: str, required_env: str):
        self.name = name
        self.description = description
        self.category = category
        self.required_env = required_env

    def __repr__(self) -> str:
        return f"ToolInfo(name={self.name!r}, category={self.category!r})"


class ToolRegistry:
    """Central registry for all enzyme engineering tools.

    Tools register themselves at import time via the ``register`` decorator
    or by calling ``ToolRegistry.register(tool_cls)`` directly.
    """

    _tools: Dict[str, type] = {}

    @classmethod
    def register(cls, tool_cls: type) -> type:
        """Register a tool class. Can be used as a decorator."""
        name = getattr(tool_cls, "name", None)
        if name is None:
            raise ValueError(f"{tool_cls} must define a 'name' class attribute")
        cls._tools[name] = tool_cls
        return tool_cls

    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Return the tool class for *name*, or ``None``."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[ToolInfo]:
        """Return metadata for every registered tool."""
        infos: List[ToolInfo] = []
        for tool_cls in cls._tools.values():
            infos.append(
                ToolInfo(
                    name=tool_cls.name,
                    description=getattr(tool_cls, "description", ""),
                    category=getattr(tool_cls, "category", ""),
                    required_env=getattr(tool_cls, "required_env", "enzymetk"),
                )
            )
        return infos

    @classmethod
    def list_names(cls) -> List[str]:
        return list(cls._tools.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registered tools (useful for testing)."""
        cls._tools.clear()
