"""
Agent tool wrappers for protein design steps: LigandMPNN.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

import pandas as pd

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.tools.base import EnzymeTool
from enzymetk.agent.schemas import ToolResult


@ToolRegistry.register
class LigandMPNNTool(EnzymeTool):
    """Redesign protein sequences around ligand binding sites using LigandMPNN."""

    name = "design_ligandmpnn"
    description = (
        "Redesign protein sequences around ligand binding sites using LigandMPNN. "
        "Requires PDB/CIF structure files and the LigandMPNN installation directory. "
        "Can fix specific residues and use ligand context for design."
    )
    category = "design"
    required_env = "ligandmpnn_env"

    def run(
        self,
        pdb_paths: List[str],
        ligand_mpnn_dir: str,
        output_dir: str,
        pdb_column: str = "pdbs",
        tmp_dir: Optional[str] = None,
        args: Optional[List[str]] = None,
        num_threads: int = 1,
    ) -> ToolResult:
        from enzymetk.inpaint_ligandMPNN_step import LigandMPNN

        df = pd.DataFrame({pdb_column: pdb_paths})
        step = LigandMPNN(
            pdb_column_name=pdb_column,
            ligand_mpnn_dir=ligand_mpnn_dir,
            output_dir=output_dir,
            tmp_dir=tmp_dir,
            args=args,
            num_threads=num_threads,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"LigandMPNN designed sequences for {len(pdb_paths)} structures",
        )
