"""Tests for the PseudoExpander class."""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from assembler.lexer import Token
from assembler.pseudo import PseudoExpander


class TestPseudoExpander:
    """Test pseudo-instruction expansion."""

    def setup_method(self):
        """Set up PseudoExpander instance for each test."""
        self.expander = PseudoExpander()

    def tokens(self, *values):
        """Helper to create token list."""
        return [Token(str(v), "UNKNOWN", 1, 0) for v in values]

    def test_nop_expansion(self):
        """Test nop -> addi x0, x0, 0."""
        result = self.expander.expand(self.tokens("nop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "addi"
        assert result[0][1].value == "x0"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "0"

    def test_mv_expansion(self):
        """Test mv rd, rs -> addi rd, rs, 0."""
        result = self.expander.expand(self.tokens("mv", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "addi"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x2"
        assert result[0][3].value == "0"

    def test_not_expansion(self):
        """Test not rd, rs -> xori rd, rs, -1."""
        result = self.expander.expand(self.tokens("not", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "xori"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x2"
        assert result[0][3].value == "-1"

    def test_neg_expansion(self):
        """Test neg rd, rs -> sub rd, x0, rs."""
        result = self.expander.expand(self.tokens("neg", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "sub"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "x2"

    def test_ret_expansion(self):
        """Test ret -> jalr x0, 0(ra)."""
        result = self.expander.expand(self.tokens("ret"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "jalr"
        assert result[0][1].value == "x0"
        assert result[0][2].value == "0(ra)"

    def test_jr_expansion(self):
        """Test jr rs -> jalr x0, 0(rs)."""
        result = self.expander.expand(self.tokens("jr", "x1"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "jalr"
        assert result[0][1].value == "x0"
        assert result[0][2].value == "0(x1)"

    def test_jalr_single_arg_expansion(self):
        """Test jalr rs -> jalr x1, 0(rs)."""
        result = self.expander.expand(self.tokens("jalr", "x1"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "jalr"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "0(x1)"

    def test_j_expansion(self):
        """Test j label -> jal x0, label."""
        result = self.expander.expand(self.tokens("j", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "jal"
        assert result[0][1].value == "x0"
        assert result[0][2].value == "loop"

    def test_jal_single_arg_expansion(self):
        """Test jal label -> jal x1, label."""
        result = self.expander.expand(self.tokens("jal", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "jal"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "loop"

    def test_beqz_expansion(self):
        """Test beqz rs, offset -> beq rs, x0, offset."""
        result = self.expander.expand(self.tokens("beqz", "x1", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "beq"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "loop"

    def test_bnez_expansion(self):
        """Test bnez rs, offset -> bne rs, x0, offset."""
        result = self.expander.expand(self.tokens("bnez", "x1", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "bne"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "loop"

    def test_blez_expansion(self):
        """Test blez rs, offset -> bge x0, rs, offset."""
        result = self.expander.expand(self.tokens("blez", "x1", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "bge"
        assert result[0][1].value == "x0"
        assert result[0][2].value == "x1"
        assert result[0][3].value == "loop"

    def test_bgez_expansion(self):
        """Test bgez rs, offset -> bge rs, x0, offset."""
        result = self.expander.expand(self.tokens("bgez", "x1", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "bge"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "loop"

    def test_bltz_expansion(self):
        """Test bltz rs, offset -> blt rs, x0, offset."""
        result = self.expander.expand(self.tokens("bltz", "x1", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "blt"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "loop"

    def test_bgtz_expansion(self):
        """Test bgtz rs, offset -> blt x0, rs, offset."""
        result = self.expander.expand(self.tokens("bgtz", "x1", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "blt"
        assert result[0][1].value == "x0"
        assert result[0][2].value == "x1"
        assert result[0][3].value == "loop"

    def test_bgt_expansion(self):
        """Test bgt rs, rt, offset -> blt rt, rs, offset."""
        result = self.expander.expand(self.tokens("bgt", "x1", "x2", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "blt"
        assert result[0][1].value == "x2"
        assert result[0][2].value == "x1"
        assert result[0][3].value == "loop"

    def test_ble_expansion(self):
        """Test ble rs, rt, offset -> bge rt, rs, offset."""
        result = self.expander.expand(self.tokens("ble", "x1", "x2", "loop"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "bge"
        assert result[0][1].value == "x2"
        assert result[0][2].value == "x1"
        assert result[0][3].value == "loop"

    def test_seqz_expansion(self):
        """Test seqz rd, rs -> sltiu rd, rs, 1."""
        result = self.expander.expand(self.tokens("seqz", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "sltiu"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x2"
        assert result[0][3].value == "1"

    def test_snez_expansion(self):
        """Test snez rd, rs -> sltu rd, x0, rs."""
        result = self.expander.expand(self.tokens("snez", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "sltu"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "x2"

    def test_sltz_expansion(self):
        """Test sltz rd, rs -> slt rd, rs, x0."""
        result = self.expander.expand(self.tokens("sltz", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "slt"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x2"
        assert result[0][3].value == "x0"

    def test_sgtz_expansion(self):
        """Test sgtz rd, rs -> slt rd, x0, rs."""
        result = self.expander.expand(self.tokens("sgtz", "x1", "x2"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "slt"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"
        assert result[0][3].value == "x2"

    def test_li_small_immediate(self):
        """Test li rd, imm with small immediate -> addi."""
        result = self.expander.expand(self.tokens("li", "x1", "10"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "addi"
        assert result[0][1].value == "x1"
        assert result[0][2].value == "x0"

    def test_li_large_immediate(self):
        """Test li rd, imm with large immediate -> lui + addi."""
        result = self.expander.expand(self.tokens("li", "x1", "0x12345"))
        assert result is not None
        assert len(result) == 2
        assert result[0][0].value == "lui"
        assert result[0][1].value == "x1"
        assert result[1][0].value == "addi"

    def test_la_expansion(self):
        """Test la rd, symbol -> auipc + addi."""
        result = self.expander.expand(self.tokens("la", "x1", "data"))
        assert result is not None
        assert len(result) == 2
        assert result[0][0].value == "auipc"
        assert result[0][1].value == "x1"
        assert result[1][0].value == "addi"

    def test_lw_pseudoinstruction(self):
        """Test lw rd, symbol -> auipc + lw."""
        result = self.expander.expand(self.tokens("lw", "x1", "data"))
        assert result is not None
        assert len(result) == 2
        assert result[0][0].value == "auipc"
        assert result[1][0].value == "lw"

    def test_sw_pseudoinstruction(self):
        """Test sw rs, symbol, rt -> auipc + sw."""
        result = self.expander.expand(self.tokens("sw", "x1", "data", "x2"))
        assert result is not None
        assert len(result) == 2
        assert result[0][0].value == "auipc"
        assert result[1][0].value == "sw"

    def test_call_expansion(self):
        """Test call offset -> auipc + jalr."""
        result = self.expander.expand(self.tokens("call", "func"))
        assert result is not None
        assert len(result) == 2
        assert result[0][0].value == "auipc"
        assert result[0][1].value == "x1"
        assert result[1][0].value == "jalr"
        assert result[1][1].value == "x1"

    def test_tail_expansion(self):
        """Test tail offset -> auipc + jalr."""
        result = self.expander.expand(self.tokens("tail", "func"))
        assert result is not None
        assert len(result) == 2
        assert result[0][0].value == "auipc"
        assert result[0][1].value == "x6"
        assert result[1][0].value == "jalr"
        assert result[1][1].value == "x0"

    def test_fence_expansion(self):
        """Test fence -> fence iorw, iorw."""
        result = self.expander.expand(self.tokens("fence"))
        assert result is not None
        assert len(result) == 1
        assert result[0][0].value == "fence"
        assert result[0][1].value == "iorw"
        assert result[0][2].value == "iorw"

    def test_invalid_pseudo_instruction(self):
        """Test that invalid pseudo-instructions return None."""
        result = self.expander.expand(self.tokens("invalid"))
        assert result is None

    def test_empty_token_list(self):
        """Test that empty token list returns None."""
        result = self.expander.expand([])
        assert result is None
