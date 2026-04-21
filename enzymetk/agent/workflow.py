"""
Workflow engine for multi-step enzyme engineering pipelines.

A Workflow is an ordered list of ToolCalls that are executed sequentially,
with intermediate results auto-saved between steps.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from enzymetk.agent.executor import execute_tool
from enzymetk.agent.persistence import ResultStore
from enzymetk.agent.schemas import ToolResult

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """A single step in a workflow."""
    tool_name: str
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Aggregated result of a full workflow execution."""
    success: bool
    steps_completed: int
    total_steps: int
    results: List[ToolResult] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def summary(self) -> str:
        lines = [f"Workflow: {self.steps_completed}/{self.total_steps} steps completed"]
        for i, r in enumerate(self.results):
            status = "OK" if r.success else "FAIL"
            lines.append(f"  Step {i+1}: [{status}] {r.summary}")
        if self.error:
            lines.append(f"  Error: {self.error}")
        return "\n".join(lines)


class Workflow:
    """Define and execute a multi-step enzyme engineering workflow.

    Parameters
    ----------
    name : str
        Human-readable workflow name.
    description : str
        What this workflow does.
    steps : list of ToolCall
        Ordered tool invocations.
    """

    def __init__(self, name: str, description: str, steps: List[ToolCall]):
        self.name = name
        self.description = description
        self.steps = steps

    def execute(
        self,
        output_dir: str = ".",
        **global_kwargs: Any,
    ) -> WorkflowResult:
        """Run all steps sequentially.

        Parameters
        ----------
        output_dir : str
            Base directory for auto-saved results.
        **global_kwargs
            Merged into every step's kwargs (step-level kwargs take precedence).
        """
        store = ResultStore(output_dir)
        results: List[ToolResult] = []

        for i, step in enumerate(self.steps):
            merged = {**global_kwargs, **step.kwargs}
            logger.info("Workflow %s: step %d/%d (%s)", self.name, i + 1, len(self.steps), step.tool_name)

            try:
                result = execute_tool(step.tool_name, **merged)
            except Exception as exc:
                logger.exception("Workflow %s failed at step %d", self.name, i + 1)
                return WorkflowResult(
                    success=False,
                    steps_completed=i,
                    total_steps=len(self.steps),
                    results=results,
                    error=str(exc),
                )

            results.append(result)
            if not result.success:
                return WorkflowResult(
                    success=False,
                    steps_completed=i + 1,
                    total_steps=len(self.steps),
                    results=results,
                    error=result.summary,
                )

        return WorkflowResult(
            success=True,
            steps_completed=len(self.steps),
            total_steps=len(self.steps),
            results=results,
        )


# ---------------------------------------------------------------------------
# Predefined workflows
# ---------------------------------------------------------------------------

enzyme_discovery_workflow = Workflow(
    name="enzyme_discovery",
    description=(
        "Discover and annotate enzymes from sequence data. "
        "Steps: BLAST search -> MMseqs clustering -> EC annotation -> Active site prediction."
    ),
    steps=[
        ToolCall("search_blast", {"mode": "blastp"}),
        ToolCall("search_mmseqs", {"method": "cluster", "args": ["--min-seq-id", "0.5", "-c", "0.8", "--cov-mode", "1"]}),
        ToolCall("annotate_ec_clean", {}),
        ToolCall("predict_active_site", {}),
    ],
)
