import unittest
import struct
import sys
import os

# Add src to path so we can import the assembler
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from assembler.lexer import Lexer
from assembler.rv32i_isa import RV32I_ISA
from assembler.assembler import Assembler

class TestDirectives(unittest.TestCase):
    def setUp(self):
        self.isa = RV32I_ISA()

    def assemble(self, code):
        lexer = Lexer(code)
        tokens = lexer.get_token_stream()
        asm = Assembler(tokens, self.isa)
        asm.first_pass()
        return asm.second_pass()

    def test_word_array(self):
        # .word 1, 2, 3 -> 12 bytes
        binary = self.assemble(".word 1, 2, 3")
        self.assertEqual(len(binary), 12)
        self.assertEqual(struct.unpack('<III', binary), (1, 2, 3))

    def test_half_array(self):
        # .half 1, 2 -> 4 bytes
        binary = self.assemble(".half 1, 2")
        self.assertEqual(len(binary), 4)
        self.assertEqual(struct.unpack('<HH', binary), (1, 2))

    def test_byte_array(self):
        # .byte 1, 2, 3, 4 -> 4 bytes
        binary = self.assemble(".byte 1, 2, 3, 4")
        self.assertEqual(binary, b'\x01\x02\x03\x04')

    def test_string_simple(self):
        # .string "ABC" -> 'ABC\0' (4 bytes)
        binary = self.assemble('.string "ABC"')
        self.assertEqual(binary, b'ABC\x00')

    def test_string_escapes(self):
        # .string "A\nB" -> 'A' '\n' 'B' '\0' (4 bytes)
        binary = self.assemble(r'.string "A\nB"')
        self.assertEqual(binary, b'A\nB\x00')

    def test_asciz(self):
        # .asciz "ABC" -> 'ABC\0'
        binary = self.assemble('.asciz "ABC"')
        self.assertEqual(binary, b'ABC\x00')

    def test_ascii(self):
        # .ascii "ABC" -> 'ABC' (no null)
        binary = self.assemble('.ascii "ABC"')
        self.assertEqual(binary, b'ABC')

    def test_space(self):
        # .space 4 -> 4 zero bytes
        binary = self.assemble('.space 4')
        self.assertEqual(binary, b'\x00\x00\x00\x00')

    def test_align(self):
        # .byte 1 (pc=1)
        # .align 2 (align to 4 bytes) -> need 3 bytes padding
        # .byte 2 (pc=5)
        code = """
        .byte 1
        .align 2
        .byte 2
        """
        binary = self.assemble(code)
        # byte 1 (1) + pad (3) + byte 2 (1) = 5 bytes
        self.assertEqual(binary, b'\x01\x00\x00\x00\x02')

if __name__ == '__main__':
    unittest.main()