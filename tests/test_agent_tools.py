"""
Tests for the agent tool wrappers: BLAST, ESM, and ActiveSitePred (Squidly).

These tests verify that:
  1. Tools are correctly registered in the ToolRegistry
  2. Input schemas validate correctly
  3. Tool wrappers properly construct DataFrames from input dicts
  4. The full tool execution pipeline works end-to-end (integration tests)
"""

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Test data shared across tests
# ---------------------------------------------------------------------------

ESTERASE_SEQUENCES = [
    {
        "id": "AXE2_TALPU",
        "sequence": "MHSKFFAASLLGLGAAAIPLEGVMEKRSCPAIHVFGARETTASPGYGSSSTVVNGVLSAYPGSTAEAINYPACGGQSSCGGASYSSSVAQGIAAVASAVNSFNSQCPSTKIVLVGYSQGGEIMDVALCGGGDPNQGYTNTAVQLSSSAVNMVKAAIFMGDPMFRAGLSYEVGTCAAGGFDQRPAGFSCPSAAKIKSYCDASDPYCCNGSNAATHQGYGSEYGSQALAFVKSKLG",
    },
    {
        "id": "AXE2_GEOSE",
        "sequence": "MKIGSGEKLLFIGDSITDCGRARPEGEGSFGALGTGYVAYVVGLLQAVYPELGIRVVNKGISGNTVRDLKARWEEDVIAQKPDWVSIMIGINDVWRQYDLPFMKEKHVYLDEYEATLRSLVLETKPLVKGIILMTPFYIEGNEQDPMRRTMDQYGRVVKQIAEETNSLFVDTQAAFNEVLKTLYPAALAWDRVHPSVAGHMILARAFLREIGFEWVRSR",
    },
    {
        "id": "AXE7A_XYLR2",
        "sequence": "MFNFAPKQTTEMKKLLFTLVFVLGSMATALAENYPYRADYLWLTVPNHADWLYKTGERAKVEVSFCLYGMPQNVEVAYEIGPDMMPATSSGKVTLKNGRAVIDMGTMKKPGFLDMRLSVDGKYQHHVKVGFSPELLKPYTKNPQDFDAFWKANLDEARKTPVSVSCNKVDKYTTDAFDCYLLKIKTDRRHSIYGYLTKPKKAGKYPVVLCPPGAGIKTIKEPMRSTFYAKNGFIRLEMEIHGLNPEMTDEQFKEITTAFDYENGYLTNGLDDRDNYYMKHVYVACVRAIDYLTSLPDWDGKNVFVQGGSQGGALSLVTAGLDPRVTACVANHPALSDMAGYLDNRAGGYPHFNRLKNMFTPEKVNTMAYYDVVNFARRITCPVYITWGYNDNVCPPTTSYIVWNLITAPKESLITPINEHWTTSETNYTQMLWLKKQVK",
    },
    {
        "id": "A0A0B8RHP0_LISMN",
        "sequence": "MKKLLFLGDSVTDAGRDFENDRELGHGYVKIIADQLEQEDVTVINRGVSANRVADLHRRIEADAISLQPDVVTIMIGINDTWFSFSRWEDTSVTAFKEVYRVILNRIKTETNAELILMEPFVLPYPEDRKEWRGDLDPKIGAVRELAAEFGATLIPLDGLMNALAIKHGPTFLAEDGVHPTKAGHEAIASTWLEFTK",
    },
]


# ---------------------------------------------------------------------------
# Unit tests: Registry and tool discovery
# ---------------------------------------------------------------------------

class TestToolRegistry:
    """Verify tools are properly registered."""

    def test_blast_registered(self):
        import enzymetk.agent.tools  # noqa: F401
        from enzymetk.agent.registry import ToolRegistry
        assert ToolRegistry.get("search_blast") is not None

    def test_esm_registered(self):
        import enzymetk.agent.tools  # noqa: F401
        from enzymetk.agent.registry import ToolRegistry
        assert ToolRegistry.get("embed_protein_esm") is not None

    def test_active_site_registered(self):
        import enzymetk.agent.tools  # noqa: F401
        from enzymetk.agent.registry import ToolRegistry
        assert ToolRegistry.get("predict_active_site") is not None

    def test_list_tools_includes_all_three(self):
        import enzymetk.agent.tools  # noqa: F401
        from enzymetk.agent.registry import ToolRegistry
        names = ToolRegistry.list_names()
        assert "search_blast" in names
        assert "embed_protein_esm" in names
        assert "predict_active_site" in names

    def test_tool_metadata(self):
        import enzymetk.agent.tools  # noqa: F401
        from enzymetk.agent.registry import ToolRegistry
        infos = ToolRegistry.list_tools()
        blast_info = [i for i in infos if i.name == "search_blast"][0]
        assert blast_info.category == "search"
        assert "BLAST" in blast_info.description or "blast" in blast_info.description.lower()


# ---------------------------------------------------------------------------
# Unit tests: DataFrame construction helpers
# ---------------------------------------------------------------------------

class TestDataFrameHelpers:
    """Verify tool base class correctly builds DataFrames from input dicts."""

    def test_sequences_to_df(self):
        from enzymetk.agent.tools.base import EnzymeTool
        df = EnzymeTool.sequences_to_df(ESTERASE_SEQUENCES[:2])
        assert list(df.columns) == ["Entry", "Sequence"]
        assert len(df) == 2
        assert df.iloc[0]["Entry"] == "AXE2_TALPU"
        assert df.iloc[1]["Entry"] == "AXE2_GEOSE"

    def test_sequences_to_df_custom_columns(self):
        from enzymetk.agent.tools.base import EnzymeTool
        df = EnzymeTool.sequences_to_df(
            ESTERASE_SEQUENCES[:1], id_column="ID", sequence_column="Seq"
        )
        assert list(df.columns) == ["ID", "Seq"]

    def test_labelled_sequences_to_df(self):
        from enzymetk.agent.tools.base import EnzymeTool
        seqs = ESTERASE_SEQUENCES[:3]
        labels = ["query", "reference", "reference"]
        df = EnzymeTool.labelled_sequences_to_df(seqs, labels)
        assert "label" in df.columns
        assert df.iloc[0]["label"] == "query"
        assert len(df) == 3


# ---------------------------------------------------------------------------
# Unit tests: Schema validation
# ---------------------------------------------------------------------------

class TestSchemas:
    """Verify Pydantic schemas validate correctly."""

    def test_sequence_record(self):
        from enzymetk.agent.schemas import SequenceRecord
        rec = SequenceRecord(id="test", sequence="MKIG")
        assert rec.id == "test"
        assert rec.sequence == "MKIG"

    def test_tool_result(self):
        from enzymetk.agent.schemas import ToolResult
        result = ToolResult(
            success=True,
            output_path="/tmp/test.pkl",
            summary="Test completed",
            num_records=10,
            columns=["Entry", "Sequence"],
        )
        assert result.success is True
        assert result.num_records == 10

    def test_sequence_input(self):
        from enzymetk.agent.schemas import SequenceInput, SequenceRecord
        inp = SequenceInput(
            sequences=[SequenceRecord(id="A", sequence="MKI")],
            id_column="Entry",
            sequence_column="Sequence",
        )
        assert len(inp.sequences) == 1


# ---------------------------------------------------------------------------
# Unit tests: Persistence
# ---------------------------------------------------------------------------

class TestPersistence:
    """Verify ResultStore saves and loads correctly."""

    def test_save_and_load(self, tmp_path):
        from enzymetk.agent.persistence import ResultStore
        store = ResultStore(str(tmp_path))
        df = pd.DataFrame({"Entry": ["A", "B"], "Sequence": ["MKI", "GEK"]})
        path = store.save(df, "test_tool")
        assert os.path.exists(path)
        loaded = store.load(path)
        assert len(loaded) == 2
        assert list(loaded.columns) == ["Entry", "Sequence"]

    def test_latest(self, tmp_path):
        from enzymetk.agent.persistence import ResultStore
        store = ResultStore(str(tmp_path))
        df = pd.DataFrame({"x": [1]})
        store.save(df, "my_tool", tag="first")
        path2 = store.save(df, "my_tool", tag="second")
        latest = store.latest("my_tool")
        assert latest == path2

    def test_list_results(self, tmp_path):
        from enzymetk.agent.persistence import ResultStore
        store = ResultStore(str(tmp_path))
        df = pd.DataFrame({"x": [1]})
        store.save(df, "tool_a")
        store.save(df, "tool_b")
        results = store.list_results()
        assert len(results) == 2


# ---------------------------------------------------------------------------
# Unit tests: Executor
# ---------------------------------------------------------------------------

class TestExecutor:
    """Verify execute_tool dispatches correctly."""

    def test_unknown_tool_raises(self):
        from enzymetk.agent.executor import execute_tool
        with pytest.raises(ValueError, match="Unknown tool"):
            execute_tool("nonexistent_tool_xyz")

    def test_execute_tool_returns_tool_result_on_failure(self):
        """If a tool's run() raises, execute_tool returns a failed ToolResult."""
        import enzymetk.agent.tools  # noqa: F401
        from enzymetk.agent.executor import execute_tool
        # Call search_blast with missing required args - should fail gracefully
        result = execute_tool("search_blast")
        assert result.success is False


# ---------------------------------------------------------------------------
# Integration tests: BLAST tool (requires diamond binary)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestSearchBlastIntegration:
    """End-to-end test of the BLAST agent tool.

    Requires Diamond BLAST to be installed in the enzymetk conda environment.
    Run with: pytest -m integration
    """

    def test_blast_with_labelled_sequences(self, tmp_path):
        from enzymetk.agent.tools.search_tools import SearchBlastTool

        sequences = [
            {"id": "AXE2_TALPU", "sequence": ESTERASE_SEQUENCES[0]["sequence"]},
            {"id": "AXE2_TALPU_ref", "sequence": ESTERASE_SEQUENCES[0]["sequence"]},
            {"id": "AXE2_GEOSE", "sequence": ESTERASE_SEQUENCES[1]["sequence"]},
            {"id": "AXE7A_XYLR2", "sequence": ESTERASE_SEQUENCES[2]["sequence"]},
            {"id": "A0A0B8RHP0_LISMN", "sequence": ESTERASE_SEQUENCES[3]["sequence"]},
        ]
        labels = ["query", "reference", "reference", "reference", "reference"]

        tool = SearchBlastTool()
        result = tool.run(
            sequences=sequences,
            labels=labels,
            tmp_dir=str(tmp_path),
        )

        assert result.success is True
        assert result.num_records > 0
        assert os.path.exists(result.output_path)
        # Load and verify the result DataFrame
        df = pd.read_pickle(result.output_path)
        assert "query" in df.columns
        assert "target" in df.columns
        assert "sequence identity" in df.columns
        print(f"BLAST returned {len(df)} hits")
        print(df.head())


# ---------------------------------------------------------------------------
# Integration tests: ESM embedding tool (requires GPU + esm package)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestEmbedProteinESMIntegration:
    """End-to-end test of the ESM-2 embedding agent tool.

    Requires fair-esm and a GPU for reasonable performance.
    Run with: pytest -m integration
    """

    def test_esm_mean_embedding(self, tmp_path):
        from enzymetk.agent.tools.embedding_tools import EmbedProteinESMTool

        tool = EmbedProteinESMTool()
        result = tool.run(
            sequences=ESTERASE_SEQUENCES,
            model="esm2_t36_3B_UR50D",
            extraction_method="mean",
            tmp_dir=str(tmp_path),
            rep_num=36,
        )

        assert result.success is True
        assert result.num_records == len(ESTERASE_SEQUENCES)
        assert os.path.exists(result.output_path)
        df = pd.read_pickle(result.output_path)
        assert "embedding" in df.columns
        assert len(df) == len(ESTERASE_SEQUENCES)
        print(f"ESM-2 embeddings shape: {df['embedding'].iloc[0].shape}")

    def test_esm_active_site_embedding(self, tmp_path):
        from enzymetk.agent.tools.embedding_tools import EmbedProteinESMTool

        tool = EmbedProteinESMTool()
        result = tool.run(
            sequences=ESTERASE_SEQUENCES,
            model="esm2_t36_3B_UR50D",
            extraction_method="active_site",
            active_site_column="ActiveSite",
            active_sites=["10", "1|2", "1", "2"],
            tmp_dir=str(tmp_path),
            rep_num=36,
        )

        assert result.success is True
        assert os.path.exists(result.output_path)
        df = pd.read_pickle(result.output_path)
        assert "active_embedding" in df.columns or "esm_embedding" in df.columns
        print(f"ESM-2 active site embeddings generated for {len(df)} sequences")


# ---------------------------------------------------------------------------
# Integration tests: ActiveSitePred/Squidly tool (requires squidly + GPU)
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.squidly
class TestActiveSitePredIntegration:
    """End-to-end test of the Squidly active site prediction agent tool.

    Requires squidly to be installed and working in its own conda environment.
    Run with: pytest -m squidly

    Note: The squidly tool requires a properly configured conda env named
    'squidly' with compatible NumPy/Numba versions and model weights.
    """

    def test_predict_active_sites(self, tmp_path):
        from enzymetk.agent.tools.prediction_tools import ActiveSitePredTool

        tool = ActiveSitePredTool()
        result = tool.run(
            sequences=ESTERASE_SEQUENCES[:2],  # Use fewer sequences for speed
            esm2_model="esm2_t36_3B_UR50D",
            tmp_dir=str(tmp_path),
            env_name="squidly",  # squidly needs its own conda env
        )

        assert result.success is True
        assert result.num_records > 0
        assert os.path.exists(result.output_path)
        df = pd.read_pickle(result.output_path)
        print(f"Active site predictions for {len(df)} sequences:")
        print(df.head())
