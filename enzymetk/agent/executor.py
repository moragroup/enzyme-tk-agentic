"""
Unified execution layer for running registered tools by name.

This module provides a single ``execute_tool`` function that resolves a tool
name from the registry and runs it with the provided keyword arguments.
"""

from __future__ import annotations
import logging
from typing import Any, Dict

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.schemas import ToolResult

logger = logging.getLogger(__name__)


def execute_tool(tool_name: str, **kwargs: Any) -> ToolResult:
    """Look up *tool_name* in the registry and execute it.

    Parameters
    ----------
    tool_name : str
        Registered name (e.g. ``"search_blast"``).
    **kwargs
        Forwarded to the tool's ``run()`` method.

    Returns
    -------
    ToolResult
        Standardised result with output path and summary.
    """
    tool_cls = ToolRegistry.get(tool_name)
    if tool_cls is None:
        available = ", ".join(ToolRegistry.list_names())
        raise ValueError(
            f"Unknown tool {tool_name!r}. Available tools: {available}"
        )

    tool = tool_cls()
    logger.info("Executing tool %s with args %s", tool_name, list(kwargs.keys()))

    try:
        result = tool.run(**kwargs)
    except Exception as exc:
        logger.exception("Tool %s failed", tool_name)
        return ToolResult(
            success=False,
            output_path="",
            summary=f"Tool {tool_name} failed: {exc}",
        )

    return result
