"""
Agent tool wrappers for prediction steps: ActiveSitePred.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.tools.base import EnzymeTool
from enzymetk.agent.schemas import ToolResult


@ToolRegistry.register
class ActiveSitePredTool(EnzymeTool):
    """Predict catalytic active sites in protein sequences using Squidly."""

    name = "predict_active_site"
    description = (
        "Predict catalytic active site residues in protein sequences using the "
        "Squidly model (built on ESM-2 embeddings). Returns residue-level "
        "predictions for each protein."
    )
    category = "prediction"
    required_env = "enzymetk"

    def run(
        self,
        sequences: List[Dict[str, str]],
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
        num_threads: int = 1,
        esm2_model: str = "esm2_t36_3B_UR50D",
        tmp_dir: Optional[str] = None,
        args: Optional[List[str]] = None,
        env_name: str = "enzymetk",
    ) -> ToolResult:
        from enzymetk.predict_catalyticsite_step import ActiveSitePred

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        step = ActiveSitePred(
            id_col=id_column,
            seq_col=sequence_column,
            num_threads=num_threads,
            esm2_model=esm2_model,
            tmp_dir=tmp_dir,
            args=args,
            env_name=env_name,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Active site predictions generated for {len(sequences)} sequences",
        )
