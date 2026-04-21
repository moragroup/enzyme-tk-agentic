"""
Auto-save persistence layer for intermediate workflow results.

Every tool execution auto-saves its DataFrame output to a timestamped pickle
file so that workflows can resume on failure and results are always recoverable.
"""

from __future__ import annotations
import os
import time
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class ResultStore:
    """Manages auto-saving of intermediate and final tool results.

    Parameters
    ----------
    base_dir : str
        Root directory for saved results. A ``enzymetk_results/`` subfolder
        is created automatically.
    """

    def __init__(self, base_dir: str = "."):
        self.results_dir = Path(base_dir) / "enzymetk_results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def save(self, df: pd.DataFrame, tool_name: str, tag: str = "") -> str:
        """Persist *df* and return the absolute path to the saved file."""
        ts = int(time.time())
        suffix = f"_{tag}" if tag else ""
        filename = f"{tool_name}{suffix}_{ts}.pkl"
        filepath = self.results_dir / filename
        df.to_pickle(str(filepath))
        logger.info("Saved %d rows to %s", len(df), filepath)
        return str(filepath.resolve())

    def load(self, path: str) -> pd.DataFrame:
        """Load a previously saved DataFrame."""
        return pd.read_pickle(path)

    def latest(self, tool_name: str) -> Optional[str]:
        """Return the path of the most recent result for *tool_name*, or None."""
        matches = sorted(
            self.results_dir.glob(f"{tool_name}_*.pkl"),
            key=os.path.getmtime,
            reverse=True,
        )
        return str(matches[0].resolve()) if matches else None

    def list_results(self) -> list[str]:
        """Return all saved result paths."""
        return [str(p.resolve()) for p in sorted(self.results_dir.glob("*.pkl"))]
