"""
Agent tool wrappers for alignment steps: ClustalOmega, FastTree.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.tools.base import EnzymeTool
from enzymetk.agent.schemas import ToolResult


@ToolRegistry.register
class ClustalOmegaTool(EnzymeTool):
    """Run multiple sequence alignment using Clustal Omega."""

    name = "align_clustalomega"
    description = (
        "Perform multiple sequence alignment (MSA) on protein sequences using "
        "Clustal Omega. Returns aligned sequences."
    )
    category = "alignment"
    required_env = "enzymetk"

    def run(
        self,
        sequences: List[Dict[str, str]],
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
        tmp_dir: Optional[str] = None,
    ) -> ToolResult:
        from enzymetk.generate_msa_step import ClustalOmega

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        step = ClustalOmega(
            id_col=id_column,
            seq_col=sequence_column,
            tmp_dir=tmp_dir,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Clustal Omega aligned {len(sequences)} sequences",
        )


@ToolRegistry.register
class FastTreeTool(EnzymeTool):
    """Generate a phylogenetic tree using FastTree."""

    name = "tree_fasttree"
    description = (
        "Generate a phylogenetic tree from aligned sequences using FastTree "
        "(WAG model). Requires a CSV with aligned sequences."
    )
    category = "alignment"
    required_env = "enzymetk"

    def run(
        self,
        sequences: List[Dict[str, str]],
        fasttree_dir: str,
        csv_file: str,
        output_dir: str,
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
    ) -> ToolResult:
        from enzymetk.generate_tree_step import FastTree

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        step = FastTree(
            fasttree_dir=fasttree_dir,
            id_col=id_column,
            seq_col=sequence_column,
            csv_file=csv_file,
            output_dir=output_dir,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"FastTree generated phylogenetic tree for {len(sequences)} sequences",
        )
