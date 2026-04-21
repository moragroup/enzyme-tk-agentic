"""
Agent tool wrappers for metagenomics steps: PoreChop, Prokka.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

import pandas as pd

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.tools.base import EnzymeTool
from enzymetk.agent.schemas import ToolResult


@ToolRegistry.register
class PoreChopTool(EnzymeTool):
    """Trim nanopore sequencing adapters using Porechop."""

    name = "metagenomics_porechop"
    description = (
        "Trim nanopore sequencing adapters from reads using Porechop. "
        "Requires input file paths and produces trimmed output files."
    )
    category = "metagenomics"
    required_env = "enzymetk"

    def run(
        self,
        input_files: List[str],
        output_files: List[str],
        porechop_dir: str,
        input_column: str = "input",
        output_column: str = "output",
        num_threads: int = 1,
    ) -> ToolResult:
        from enzymetk.metagenomics_porechop_trim_reads_step import PoreChop

        df = pd.DataFrame({input_column: input_files, output_column: output_files})
        step = PoreChop(
            porechop_dir=porechop_dir,
            input_column_name=input_column,
            output_column_name=output_column,
            num_threads=num_threads,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Porechop trimmed {len(input_files)} read files",
        )


@ToolRegistry.register
class ProkkaTool(EnzymeTool):
    """Annotate genome contigs using Prokka."""

    name = "metagenomics_prokka"
    description = (
        "Annotate assembled genome contigs (gene calling) using Prokka. "
        "Requires contig file paths and produces gene annotation files."
    )
    category = "metagenomics"
    required_env = "enzymetk"

    def run(
        self,
        input_files: List[str],
        name: str,
        porechop_dir: str,
        output_dir: str,
        input_column: str = "input",
        num_threads: int = 1,
    ) -> ToolResult:
        from enzymetk.metagenomics_prokka_annotate_genes import Prokka

        df = pd.DataFrame({input_column: input_files})
        step = Prokka(
            porechop_dir=porechop_dir,
            name=name,
            input_column_name=input_column,
            output_dir=output_dir,
            num_threads=num_threads,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Prokka annotated {len(input_files)} contig files",
        )
