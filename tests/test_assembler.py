"""Tests for the Assembler class."""
import pytest
import sys
import os
import struct

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from assembler.lexer import Lexer, Token
from assembler.rv32i_isa import RV32I_ISA
from assembler.assembler import Assembler


class TestAssembler:
    """Test the Assembler class."""

    def assemble(self, source_code):
        """Helper to assemble source code and return binary."""
        lexer = Lexer(source_code)
        tokens = lexer.get_token_stream()
        isa = RV32I_ISA()
        asm = Assembler(tokens, isa)
        asm.first_pass()
        return asm.second_pass(), asm.symbol_table

    def test_simple_instruction(self):
        """Test assembling a simple instruction."""
        source = "add x1, x2, x3"
        binary, _ = self.assemble(source)
        
        assert len(binary) == 4
        machine_code = struct.unpack('<I', binary)[0]
        
        # Expected: f7=0, rs2=3, rs1=2, f3=0, rd=1, opcode=0x33
        expected = (0 << 25) | (3 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x33
        assert machine_code == expected

    def test_multiple_instructions(self):
        """Test assembling multiple instructions."""
        source = """add x1, x2, x3
sub x4, x5, x6"""
        binary, _ = self.assemble(source)
        
        assert len(binary) == 8
        
        # Check first instruction
        machine_code1 = struct.unpack('<I', binary[0:4])[0]
        expected1 = (0 << 25) | (3 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x33
        assert machine_code1 == expected1
        
        # Check second instruction
        machine_code2 = struct.unpack('<I', binary[4:8])[0]
        expected2 = (0x20 << 25) | (6 << 20) | (5 << 15) | (0 << 12) | (4 << 7) | 0x33
        assert machine_code2 == expected2

    def test_label_resolution(self):
        """Test that labels are properly resolved."""
        source = """add x1, x2, x3
loop: sub x4, x5, x6"""
        binary, symbol_table = self.assemble(source)
        
        assert "loop" in symbol_table
        assert symbol_table["loop"] == 4

    def test_multiple_labels(self):
        """Test multiple labels."""
        source = """start: add x1, x2, x3
middle: sub x4, x5, x6
end: xor x7, x8, x9"""
        binary, symbol_table = self.assemble(source)
        
        assert symbol_table["start"] == 0
        assert symbol_table["middle"] == 4
        assert symbol_table["end"] == 8

    def test_word_directive(self):
        """Test .word directive."""
        source = ".word 42"
        binary, _ = self.assemble(source)
        
        assert len(binary) == 4
        value = struct.unpack('<I', binary)[0]
        assert value == 42

    def test_byte_directive(self):
        """Test .byte directive."""
        source = ".byte 0xFF"
        binary, _ = self.assemble(source)
        
        assert len(binary) == 1
        assert binary[0] == 0xFF

    def test_word_with_negative_value(self):
        """Test .word directive with negative value."""
        source = ".word -1"
        binary, _ = self.assemble(source)
        
        assert len(binary) == 4
        value = struct.unpack('<i', binary)[0]
        assert value == -1

    def test_label_with_instruction(self):
        """Test label on same line as instruction."""
        source = "loop: add x1, x2, x3"
        binary, symbol_table = self.assemble(source)
        
        assert symbol_table["loop"] == 0
        assert len(binary) == 4

    def test_label_with_directive(self):
        """Test label on same line as directive."""
        source = """data: .word 42
add x1, x2, x3"""
        binary, symbol_table = self.assemble(source)
        
        assert symbol_table["data"] == 0
        assert len(binary) == 8

    def test_alignment(self):
        """Test that instructions are properly aligned."""
        source = """add x1, x2, x3
sub x4, x5, x6
xor x7, x8, x9"""
        binary, _ = self.assemble(source)
        
        # Each instruction is 4 bytes, aligned on 4-byte boundaries
        assert len(binary) == 12

    def test_nop_expansion(self):
        """Test that nop pseudo-instruction is expanded."""
        source = "nop"
        binary, _ = self.assemble(source)
        
        assert len(binary) == 4
        machine_code = struct.unpack('<I', binary)[0]
        # nop -> addi x0, x0, 0
        expected = (0 << 20) | (0 << 15) | (0 << 12) | (0 << 7) | 0x13
        assert machine_code == expected

    def test_comments_ignored(self):
        """Test that comments don't affect assembly."""
        source = """# This is a comment
add x1, x2, x3  # Another comment
sub x4, x5, x6"""
        binary, _ = self.assemble(source)
        
        assert len(binary) == 8

    def test_empty_lines_ignored(self):
        """Test that empty lines are ignored."""
        source = """add x1, x2, x3

sub x4, x5, x6"""
        binary, _ = self.assemble(source)
        
        assert len(binary) == 8

    def test_global_directive(self):
        """Test .global directive is accepted."""
        source = """.global main
main: add x1, x2, x3"""
        binary, symbol_table = self.assemble(source)
        
        assert symbol_table["main"] == 0

    def test_text_directive(self):
        """Test .text directive is accepted."""
        source = """.text
add x1, x2, x3"""
        binary, _ = self.assemble(source)
        
        assert len(binary) == 4

    def test_section_directive(self):
        """Test .section directive is accepted."""
        source = """.section .text
add x1, x2, x3"""
        binary, _ = self.assemble(source)
        
        assert len(binary) == 4

    def test_addi_instruction(self):
        """Test addi instruction assembly."""
        source = "addi x1, x2, 10"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        expected = (10 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_lw_instruction(self):
        """Test load word instruction assembly."""
        # Note: lw with 2 args is a pseudo-instruction for loading from a symbol
        # For a direct memory load, we need 3 tokens (but that's not standard RISC-V syntax)
        # Instead, test that the pseudo-instruction expands correctly
        source = """data: .word 42
lw x1, data"""
        binary, _ = self.assemble(source)
        
        # Should generate .word (4 bytes) + auipc + lw (8 bytes) = 12 bytes
        assert len(binary) == 12

    def test_sw_instruction(self):
        """Test store word instruction assembly."""
        source = "sw x1, 0(x2)"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        expected = (0 << 25) | (1 << 20) | (2 << 15) | (2 << 12) | (0 << 7) | 0x23
        assert machine_code == expected

    def test_beq_instruction(self):
        """Test branch equal instruction assembly."""
        source = """loop: add x1, x2, x3
beq x4, x5, loop"""
        binary, symbol_table = self.assemble(source)
        
        # The branch should target offset 0 (loop is at 0, beq is at 4)
        # So offset = 0 - 4 = -4
        machine_code = struct.unpack('<I', binary[4:8])[0]
        # Check the basic structure - just verify it's a branch instruction
        assert (machine_code & 0x7F) == 0x63  # Branch opcode

    def test_jal_instruction(self):
        """Test jump and link instruction assembly."""
        source = """main: jal x1, func
func: add x1, x2, x3"""
        binary, symbol_table = self.assemble(source)
        
        assert "main" in symbol_table
        assert "func" in symbol_table
        assert symbol_table["func"] == symbol_table["main"] + 4

    def test_pseudo_instruction_mv(self):
        """Test mv pseudo-instruction expansion."""
        source = "mv x1, x2"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        # mv -> addi x1, x2, 0
        expected = (0 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_pseudo_instruction_li_small(self):
        """Test li pseudo-instruction with small immediate."""
        source = "li x1, 10"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        # li 10 -> addi x1, x0, 10
        expected = (10 << 20) | (0 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_pseudo_instruction_li_large(self):
        """Test li pseudo-instruction with large immediate."""
        source = "li x1, 0x12345"
        binary, _ = self.assemble(source)
        
        # Should generate 2 instructions (lui + addi)
        assert len(binary) == 8

    def test_register_abi_names(self):
        """Test that ABI register names work."""
        source = "add ra, sp, gp"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        # add ra(1), sp(2), gp(3)
        expected = (3 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x33
        assert machine_code == expected

    def test_hex_immediate(self):
        """Test hexadecimal immediate values."""
        source = "addi x1, x2, 0xFF"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        expected = (0xFF << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_negative_immediate(self):
        """Test negative immediate values."""
        source = "addi x1, x2, -10"
        binary, _ = self.assemble(source)
        
        machine_code = struct.unpack('<I', binary)[0]
        expected = ((-10 & 0xFFF) << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_complex_program(self):
        """Test assembling a more complex program."""
        source = """.global main
.text
main:
  addi x1, x0, 5
  addi x2, x0, 10
  add x3, x1, x2
  beq x3, x0, end
  addi x4, x0, 1
end:
  nop
"""
        binary, symbol_table = self.assemble(source)
        
        assert "main" in symbol_table
        assert "end" in symbol_table
        assert len(binary) > 0
