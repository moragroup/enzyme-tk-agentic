"""
Agent tool wrappers for molecular docking steps: Boltz, Chai, Vina.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.tools.base import EnzymeTool
from enzymetk.agent.schemas import ToolResult

import pandas as pd


@ToolRegistry.register
class DockBoltzTool(EnzymeTool):
    """Protein-ligand docking with affinity prediction using Boltz."""

    name = "dock_boltz"
    description = (
        "Perform protein-ligand docking with affinity prediction using the Boltz model. "
        "Requires protein sequences and substrate SMILES. Generates docked poses and "
        "binding affinity predictions."
    )
    category = "docking"
    required_env = "enzymetk"

    def run(
        self,
        sequences: List[Dict[str, str]],
        substrates: List[str],
        intermediates: List[str],
        output_dir: str,
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
        substrate_column: str = "Substrate",
        intermediate_column: str = "Intermediate",
        num_threads: int = 1,
        args: Optional[List[str]] = None,
    ) -> ToolResult:
        from enzymetk.dock_boltz_step import Boltz

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        df[substrate_column] = substrates
        df[intermediate_column] = intermediates

        step = Boltz(
            id_col=id_column,
            seq_col=sequence_column,
            substrate_col=substrate_column,
            intermediate_col=intermediate_column,
            output_dir=output_dir,
            num_threads=num_threads,
            args=args,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Boltz docking completed for {len(sequences)} sequences",
        )


@ToolRegistry.register
class DockChaiTool(EnzymeTool):
    """Protein-ligand docking using Chai-lab."""

    name = "dock_chai"
    description = (
        "Perform protein-ligand docking using Chai-lab. Requires protein sequences, "
        "substrate SMILES, and optional cofactor SMILES. Produces docked structures."
    )
    category = "docking"
    required_env = "enzymetk"

    def run(
        self,
        sequences: List[Dict[str, str]],
        substrates: List[str],
        cofactors: Optional[List[str]] = None,
        output_dir: str = "tmp/",
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
        substrate_column: str = "Substrate",
        cofactor_column: str = "Cofactor",
        num_threads: int = 1,
    ) -> ToolResult:
        from enzymetk.dock_chai_step import Chai

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        df[substrate_column] = substrates
        df[cofactor_column] = cofactors if cofactors else [""] * len(sequences)

        step = Chai(
            id_col=id_column,
            seq_col=sequence_column,
            substrate_col=substrate_column,
            cofactor_col=cofactor_column,
            output_dir=output_dir,
            num_threads=num_threads,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Chai docking completed for {len(sequences)} sequences in {output_dir}",
        )


@ToolRegistry.register
class DockVinaTool(EnzymeTool):
    """Molecular docking using AutoDock Vina."""

    name = "dock_vina"
    description = (
        "Dock substrates into protein active sites using AutoDock Vina. Requires "
        "protein structures (or sequences for folding), substrate SMILES, and "
        "active site residue definitions."
    )
    category = "docking"
    required_env = "enzymetk"

    def run(
        self,
        ids: List[str],
        structures: List[Optional[str]],
        sequences: List[str],
        substrates: List[str],
        substrate_names: List[str],
        active_site_residues: List[str],
        output_dir: str = "tmp/",
        id_column: str = "Entry",
        structure_column: str = "structure",
        sequence_column: str = "Sequence",
        substrate_column: str = "Substrate",
        substrate_name_column: str = "name",
        active_site_column: str = "residues",
        num_threads: int = 1,
    ) -> ToolResult:
        from enzymetk.dock_vina_step import Vina

        df = pd.DataFrame({
            id_column: ids,
            structure_column: structures,
            active_site_column: active_site_residues,
            substrate_name_column: substrate_names,
            sequence_column: sequences,
            substrate_column: substrates,
        })

        step = Vina(
            id_col=id_column,
            structure_col=structure_column,
            sequence_col=sequence_column,
            substrate_col=substrate_column,
            substrate_name_col=substrate_name_column,
            active_site_col=active_site_column,
            output_dir=output_dir,
            num_threads=num_threads,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"Vina docking completed for {len(ids)} structures in {output_dir}",
        )
