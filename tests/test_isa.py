"""Tests for the RV32I_ISA class."""
import pytest
import sys
import os
import struct

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from assembler.lexer import Token
from assembler.rv32i_isa import RV32I_ISA


class TestRV32I_ISA:
    """Test the RISC-V ISA encoding."""

    def setup_method(self):
        """Set up ISA instance for each test."""
        self.isa = RV32I_ISA()

    def test_register_mapping_x_names(self):
        """Test register mapping with x0-x31 names."""
        assert self.isa.get_reg("x0") == 0
        assert self.isa.get_reg("x1") == 1
        assert self.isa.get_reg("x31") == 31

    def test_register_mapping_abi_names(self):
        """Test register mapping with ABI names."""
        assert self.isa.get_reg("zero") == 0
        assert self.isa.get_reg("ra") == 1
        assert self.isa.get_reg("sp") == 2
        assert self.isa.get_reg("gp") == 3
        assert self.isa.get_reg("a0") == 10
        assert self.isa.get_reg("a7") == 17

    def test_invalid_register(self):
        """Test that invalid register names raise errors."""
        with pytest.raises(ValueError):
            self.isa.get_reg("invalid")

    def test_r_type_instruction_info(self):
        """Test getting info for R-type instructions."""
        opcode, f3, f7, fmt = self.isa.get_info("add")
        assert opcode == 0x33
        assert f3 == 0x0
        assert f7 == 0x00
        assert fmt == "R"

    def test_i_type_instruction_info(self):
        """Test getting info for I-type instructions."""
        opcode, f3, f7, fmt = self.isa.get_info("addi")
        assert opcode == 0x13
        assert f3 == 0x0
        assert f7 is None
        assert fmt == "I"

    def test_s_type_instruction_info(self):
        """Test getting info for S-type instructions."""
        opcode, f3, f7, fmt = self.isa.get_info("sw")
        assert opcode == 0x23
        assert f3 == 0x2
        assert fmt == "S"

    def test_b_type_instruction_info(self):
        """Test getting info for B-type instructions."""
        opcode, f3, f7, fmt = self.isa.get_info("beq")
        assert opcode == 0x63
        assert f3 == 0x0
        assert fmt == "B"

    def test_u_type_instruction_info(self):
        """Test getting info for U-type instructions."""
        opcode, f3, f7, fmt = self.isa.get_info("lui")
        assert opcode == 0x37
        assert fmt == "U"

    def test_j_type_instruction_info(self):
        """Test getting info for J-type instructions."""
        opcode, f3, f7, fmt = self.isa.get_info("jal")
        assert opcode == 0x6f
        assert fmt == "J"

    def test_unknown_instruction(self):
        """Test that unknown instructions raise errors."""
        with pytest.raises(ValueError):
            self.isa.get_info("invalid")

    def test_r_type_encoding_add(self):
        """Test R-type encoding for add instruction."""
        tokens = [Token("add", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("x3", "REG", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # add x1, x2, x3 should encode correctly
        # f7=0, rs2=3, rs1=2, f3=0, rd=1, opcode=0x33
        expected = (0 << 25) | (3 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x33
        assert machine_code == expected

    def test_r_type_encoding_sub(self):
        """Test R-type encoding for sub instruction."""
        tokens = [Token("sub", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("x3", "REG", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # sub x1, x2, x3 should encode correctly
        # f7=0x20, rs2=3, rs1=2, f3=0, rd=1, opcode=0x33
        expected = (0x20 << 25) | (3 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x33
        assert machine_code == expected

    def test_i_type_encoding_addi(self):
        """Test I-type encoding for addi instruction."""
        tokens = [Token("addi", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("10", "IMM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # addi x1, x2, 10 should encode correctly
        # imm=10, rs1=2, f3=0, rd=1, opcode=0x13
        expected = (10 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_i_type_encoding_negative_immediate(self):
        """Test I-type encoding with negative immediate."""
        tokens = [Token("addi", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("-10", "IMM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # addi x1, x2, -10 should encode correctly
        # imm=-10, rs1=2, f3=0, rd=1, opcode=0x13
        expected = ((-10 & 0xFFF) << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_i_type_lw_encoding(self):
        """Test I-type load word encoding."""
        tokens = [Token("lw", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("8(x2)", "MEM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # lw x1, 8(x2) should encode correctly
        # imm=8, rs1=2, f3=2, rd=1, opcode=0x03
        expected = (8 << 20) | (2 << 15) | (2 << 12) | (1 << 7) | 0x03
        assert machine_code == expected

    def test_s_type_encoding_sw(self):
        """Test S-type encoding for sw instruction."""
        tokens = [Token("sw", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("8(x2)", "MEM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # sw x1, 8(x2)
        # imm=8: imm11_5=0, imm4_0=8, rs2=1, rs1=2, f3=2, opcode=0x23
        expected = (0 << 25) | (1 << 20) | (2 << 15) | (2 << 12) | (8 << 7) | 0x23
        assert machine_code == expected

    def test_b_type_encoding_beq(self):
        """Test B-type encoding for beq instruction."""
        tokens = [Token("beq", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("loop", "LABEL", 1, 0)]
        symbol_table = {"loop": 8}
        machine_code = self.isa.encode(tokens, 0, symbol_table)
        
        # beq x1, x2, loop with offset=8
        # offset should be 8 >> 1 = 4
        offset = 8
        imm = offset >> 1
        imm_12 = (imm >> 11) & 1
        imm_10_5 = (imm >> 4) & 0x3F
        imm_4_1 = imm & 0xF
        imm_11 = (imm >> 10) & 1
        
        encoded_imm = (imm_12 << 31) | (imm_10_5 << 25) | (imm_4_1 << 8) | (imm_11 << 7)
        expected = encoded_imm | (2 << 20) | (1 << 15) | (0 << 12) | 0x63
        assert machine_code == expected

    def test_u_type_encoding_lui(self):
        """Test U-type encoding for lui instruction."""
        tokens = [Token("lui", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("0x12345", "IMM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        # lui x1, 0x12345
        expected = ((0x12345 & 0xFFFFF) << 12) | (1 << 7) | 0x37
        assert machine_code == expected

    def test_j_type_encoding_jal(self):
        """Test J-type encoding for jal instruction."""
        tokens = [Token("jal", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("main", "LABEL", 1, 0)]
        symbol_table = {"main": 100}
        machine_code = self.isa.encode(tokens, 0, symbol_table)
        
        # jal x1, main with offset=100
        offset = 100
        imm = offset >> 1
        imm_20 = (imm >> 19) & 1
        imm_10_1 = imm & 0x3FF
        imm_11 = (imm >> 10) & 1
        imm_19_12 = (imm >> 11) & 0xFF
        
        encoded_imm = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12)
        expected = encoded_imm | (1 << 7) | 0x6f
        assert machine_code == expected

    def test_immediate_resolution_decimal(self):
        """Test that decimal immediates are resolved correctly."""
        tokens = [Token("addi", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("42", "IMM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        expected = (42 << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_immediate_resolution_hex(self):
        """Test that hexadecimal immediates are resolved correctly."""
        tokens = [Token("addi", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("0xFF", "IMM", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        expected = (0xFF << 20) | (2 << 15) | (0 << 12) | (1 << 7) | 0x13
        assert machine_code == expected

    def test_label_not_found(self):
        """Test that missing labels raise errors."""
        tokens = [Token("beq", "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                  Token("x2", "REG", 1, 0), Token("missing", "LABEL", 1, 0)]
        
        with pytest.raises(ValueError):
            self.isa.encode(tokens, 0, {})

    def test_load_instructions(self):
        """Test encoding of all load instructions."""
        load_instr = [("lw", 0x2), ("lh", 0x1), ("lb", 0x0), ("lhu", 0x5), ("lbu", 0x4)]
        
        for instr, f3 in load_instr:
            tokens = [Token(instr, "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                      Token("0(x2)", "MEM", 1, 0)]
            machine_code = self.isa.encode(tokens, 0, {})
            expected = (0 << 20) | (2 << 15) | (f3 << 12) | (1 << 7) | 0x03
            assert machine_code == expected

    def test_store_instructions(self):
        """Test encoding of all store instructions."""
        store_instr = [("sw", 0x2), ("sh", 0x1), ("sb", 0x0)]
        
        for instr, f3 in store_instr:
            tokens = [Token(instr, "INSTR", 1, 0), Token("x1", "REG", 1, 0),
                      Token("0(x2)", "MEM", 1, 0)]
            machine_code = self.isa.encode(tokens, 0, {})
            expected = (0 << 25) | (1 << 20) | (2 << 15) | (f3 << 12) | (0 << 7) | 0x23
            assert machine_code == expected

    def test_ecall_encoding(self):
        """Test encoding of ecall instruction."""
        tokens = [Token("ecall", "INSTR", 1, 0)]
        machine_code = self.isa.encode(tokens, 0, {})
        
        expected = (0 << 20) | (0 << 15) | (0 << 12) | (0 << 7) | 0x73
        assert machine_code == expected
