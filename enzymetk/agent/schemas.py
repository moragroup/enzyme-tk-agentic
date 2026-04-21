"""
Pydantic schemas for standardized input/output validation across all enzyme tools.

These schemas define the data contracts that LangChain tools use to validate
parameters and format results.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class SequenceRecord(BaseModel):
    """A single protein sequence with identifier."""
    id: str = Field(description="Unique identifier for this sequence")
    sequence: str = Field(description="Amino acid sequence (single-letter code)")

class SequenceInput(BaseModel):
    """Standard input for tools that operate on protein sequences."""
    sequences: List[SequenceRecord] = Field(
        description="List of protein sequences with IDs"
    )
    id_column: str = Field(default="Entry", description="Column name for sequence IDs")
    sequence_column: str = Field(default="Sequence", description="Column name for sequences")

class LabelledSequenceInput(SequenceInput):
    """Sequences with an additional label column (e.g. query vs reference)."""
    labels: Optional[List[str]] = Field(
        default=None, description="Label per sequence (e.g. 'query' or 'reference')"
    )
    label_column: str = Field(default="label", description="Column name for labels")

class MoleculeInput(BaseModel):
    """Input for tools that operate on small molecules (SMILES)."""
    smiles: List[str] = Field(description="SMILES strings for molecules or reactions")
    ids: Optional[List[str]] = Field(default=None, description="Optional IDs for each molecule")
    id_column: str = Field(default="Entry", description="Column name for IDs")
    smiles_column: str = Field(default="SMILES", description="Column name for SMILES")

class StructureInput(BaseModel):
    """Input for tools that operate on protein structures (PDB/CIF files)."""
    structure_paths: List[str] = Field(description="Paths to PDB or CIF files")
    ids: Optional[List[str]] = Field(default=None, description="Optional IDs for each structure")
    id_column: str = Field(default="Entry", description="Column name for IDs")
    structure_column: str = Field(default="structure", description="Column name for structure paths")

class DockingInput(BaseModel):
    """Input for molecular docking tools."""
    sequences: List[SequenceRecord] = Field(description="Protein sequences")
    substrates: List[str] = Field(description="Substrate SMILES strings")
    id_column: str = Field(default="Entry", description="Column name for IDs")
    sequence_column: str = Field(default="Sequence", description="Column name for sequences")
    substrate_column: str = Field(default="Substrate", description="Column name for substrates")
    output_dir: str = Field(description="Directory for docking output files")


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class ToolResult(BaseModel):
    """Base result returned by every tool."""
    success: bool = Field(description="Whether the tool executed successfully")
    output_path: str = Field(description="Path to the saved result file (pickle)")
    summary: str = Field(description="Human-readable summary of the result")
    num_records: int = Field(default=0, description="Number of records in the result")
    columns: List[str] = Field(default_factory=list, description="Column names in the result DataFrame")

class SearchResult(ToolResult):
    """Result from sequence/structure similarity search."""
    num_hits: int = Field(default=0, description="Total number of hits found")

class EmbeddingResult(ToolResult):
    """Result from embedding tools."""
    embedding_dimension: int = Field(default=0, description="Dimensionality of each embedding vector")
    model_name: str = Field(default="", description="Name of the model used")

class AnnotationResult(ToolResult):
    """Result from EC annotation tools."""
    annotation_column: str = Field(default="predicted_ecs", description="Column containing annotations")

class DockingResult(ToolResult):
    """Result from docking tools."""
    num_poses: int = Field(default=0, description="Total number of docking poses generated")

class AlignmentResult(ToolResult):
    """Result from MSA / phylogenetic tree tools."""
    alignment_format: str = Field(default="fasta", description="Format of the alignment output")

class DesignResult(ToolResult):
    """Result from protein design tools."""
    num_designs: int = Field(default=0, description="Number of designed sequences generated")

class SimilarityResult(ToolResult):
    """Result from similarity calculation tools."""
    metric: str = Field(default="tanimoto", description="Similarity metric used")
