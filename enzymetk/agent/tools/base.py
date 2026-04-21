"""
Base class for all enzyme agent tools.

Provides helper methods shared by every tool wrapper:
  - DataFrame construction from sequence/molecule lists
  - Auto-save of results via ResultStore
  - Standardised ToolResult formatting
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from enzymetk.agent.persistence import ResultStore
from enzymetk.agent.schemas import ToolResult

logger = logging.getLogger(__name__)

# Shared result store (auto-saves to ./enzymetk_results/)
_default_store = ResultStore(".")


class EnzymeTool:
    """Mixin / base for enzyme tool wrappers.

    Subclasses must set ``name``, ``description``, and ``category`` class
    attributes and implement ``run(**kwargs) -> ToolResult``.
    """

    name: str = ""
    description: str = ""
    category: str = ""
    required_env: str = "enzymetk"

    # ------------------------------------------------------------------
    # DataFrame helpers
    # ------------------------------------------------------------------

    @staticmethod
    def sequences_to_df(
        sequences: List[Dict[str, str]],
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
    ) -> pd.DataFrame:
        """Convert a list of ``{id, sequence}`` dicts to a DataFrame."""
        rows = [[s["id"], s["sequence"]] for s in sequences]
        return pd.DataFrame(rows, columns=[id_column, sequence_column])

    @staticmethod
    def labelled_sequences_to_df(
        sequences: List[Dict[str, str]],
        labels: List[str],
        id_column: str = "Entry",
        label_column: str = "label",
        sequence_column: str = "Sequence",
    ) -> pd.DataFrame:
        rows = [[s["id"], lbl, s["sequence"]] for s, lbl in zip(sequences, labels)]
        return pd.DataFrame(rows, columns=[id_column, label_column, sequence_column])

    @staticmethod
    def molecules_to_df(
        smiles: List[str],
        ids: Optional[List[str]] = None,
        id_column: str = "Entry",
        smiles_column: str = "SMILES",
    ) -> pd.DataFrame:
        if ids is None:
            ids = [f"mol_{i}" for i in range(len(smiles))]
        return pd.DataFrame({id_column: ids, smiles_column: smiles})

    @staticmethod
    def structures_to_df(
        paths: List[str],
        ids: Optional[List[str]] = None,
        id_column: str = "Entry",
        structure_column: str = "structure",
    ) -> pd.DataFrame:
        if ids is None:
            ids = [f"struct_{i}" for i in range(len(paths))]
        return pd.DataFrame({id_column: ids, structure_column: paths})

    # ------------------------------------------------------------------
    # Result helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_result(
        df: pd.DataFrame,
        tool_name: str,
        summary: str,
        store: Optional[ResultStore] = None,
        **extra_fields: Any,
    ) -> ToolResult:
        """Save *df* and return a ``ToolResult``."""
        store = store or _default_store
        path = store.save(df, tool_name)
        return ToolResult(
            success=True,
            output_path=path,
            summary=summary,
            num_records=len(df),
            columns=list(df.columns),
            **extra_fields,
        )
