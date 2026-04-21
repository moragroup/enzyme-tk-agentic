"""
Agent tool wrappers for EC annotation steps: CLEAN, CREEP, ProteInfer.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from enzymetk.agent.registry import ToolRegistry
from enzymetk.agent.tools.base import EnzymeTool
from enzymetk.agent.schemas import ToolResult


@ToolRegistry.register
class AnnotateECCleanTool(EnzymeTool):
    """Predict EC numbers using CLEAN (Contrastive Learning for Enzyme Annotation)."""

    name = "annotate_ec_clean"
    description = (
        "Predict enzyme commission (EC) numbers for protein sequences using CLEAN. "
        "Requires a CLEAN installation directory. Returns predicted EC numbers with "
        "confidence scores. Good for high-throughput EC annotation."
    )
    category = "annotation"
    required_env = "clean"

    def run(
        self,
        sequences: List[Dict[str, str]],
        clean_dir: str,
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
        num_threads: int = 1,
        ec1_filter: Optional[List[str]] = None,
        ec2_filter: Optional[List[str]] = None,
        ec3_filter: Optional[List[str]] = None,
        ec4_filter: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        env_name: str = "clean",
    ) -> ToolResult:
        from enzymetk.annotateEC_CLEAN_step import CLEAN

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        step = CLEAN(
            id_col=id_column,
            seq_col=sequence_column,
            clean_dir=clean_dir,
            num_threads=num_threads,
            ec1_filter=ec1_filter,
            ec2_filter=ec2_filter,
            ec3_filter=ec3_filter,
            ec4_filter=ec4_filter,
            env_name=env_name,
            args=args,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"CLEAN annotated {len(result_df)} sequences with EC numbers",
        )


@ToolRegistry.register
class AnnotateECCreepTool(EnzymeTool):
    """Annotate EC numbers using CREEP cross-modal retrieval."""

    name = "annotate_ec_creep"
    description = (
        "Annotate enzyme commission numbers using CREEP cross-modal retrieval "
        "(reaction-to-protein similarity). Requires CREEP installation directory "
        "and cache directory."
    )
    category = "annotation"
    required_env = "CREEP"

    def run(
        self,
        sequences: List[Dict[str, str]],
        creep_dir: str,
        creep_cache_dir: str,
        modality: str,
        reference_modality: str,
        id_column: str = "Entry",
        value_column: str = "Sequence",
        env_name: str = "CREEP",
        args_extract: Optional[List[str]] = None,
        args_retrieval: Optional[List[str]] = None,
    ) -> ToolResult:
        from enzymetk.annotateEC_CREEP_step import CREEP

        df = self.sequences_to_df(sequences, id_column, value_column)
        step = CREEP(
            id_col=id_column,
            value_col=value_column,
            CREEP_dir=creep_dir,
            CREEP_cache_dir=creep_cache_dir,
            modality=modality,
            reference_modality=reference_modality,
            env_name=env_name,
            args_extract=args_extract,
            args_retrieval=args_retrieval,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"CREEP annotated {len(result_df)} sequences",
        )


@ToolRegistry.register
class AnnotateECProteInferTool(EnzymeTool):
    """Predict EC numbers from protein sequences using ProteInfer."""

    name = "annotate_ec_proteinfer"
    description = (
        "Predict enzyme commission (EC) numbers using ProteInfer deep learning model. "
        "Requires a ProteInfer installation directory with model weights."
    )
    category = "annotation"
    required_env = "proteinfer"

    def run(
        self,
        sequences: List[Dict[str, str]],
        proteinfer_dir: str,
        id_column: str = "Entry",
        sequence_column: str = "Sequence",
        num_threads: int = 1,
        ec1_filter: Optional[List[str]] = None,
        ec2_filter: Optional[List[str]] = None,
        ec3_filter: Optional[List[str]] = None,
        ec4_filter: Optional[List[str]] = None,
        env_name: str = "proteinfer",
        args: Optional[List[str]] = None,
    ) -> ToolResult:
        from enzymetk.annotateEC_proteinfer_step import ProteInfer

        df = self.sequences_to_df(sequences, id_column, sequence_column)
        step = ProteInfer(
            id_col=id_column,
            seq_col=sequence_column,
            proteinfer_dir=proteinfer_dir,
            num_threads=num_threads,
            ec1_filter=ec1_filter,
            ec2_filter=ec2_filter,
            ec3_filter=ec3_filter,
            ec4_filter=ec4_filter,
            env_name=env_name,
            args=args,
        )
        result_df = step.execute(df)
        return self.make_result(
            result_df,
            self.name,
            f"ProteInfer annotated {len(result_df)} sequences with EC numbers",
        )
