"""Tests for the Lexer class."""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from assembler.lexer import Lexer, Token


class TestLexer:
    """Test the Lexer tokenization."""

    def test_basic_tokenization(self):
        """Test basic tokenization of a simple instruction."""
        source = "add x1, x2, x3"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 4
        assert tokens[0].value == "add"
        assert tokens[1].value == "x1"
        assert tokens[2].value == "x2"
        assert tokens[3].value == "x3"

    def test_comma_handling(self):
        """Test that commas are properly handled as delimiters."""
        source = "add x1,x2,x3"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 4
        assert [t.value for t in tokens] == ["add", "x1", "x2", "x3"]

    def test_comment_stripping(self):
        """Test that comments are properly stripped."""
        source = "add x1, x2, x3  # This is a comment"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 4
        assert tokens[0].value == "add"

    def test_multiple_lines(self):
        """Test tokenization across multiple lines."""
        source = """add x1, x2, x3
sub x4, x5, x6
xor x7, x8, x9"""
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 12
        assert tokens[0].value == "add"
        assert tokens[4].value == "sub"
        assert tokens[8].value == "xor"

    def test_empty_lines_ignored(self):
        """Test that empty lines are ignored."""
        source = """add x1, x2, x3

sub x4, x5, x6"""
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 8

    def test_line_numbers(self):
        """Test that line numbers are correctly assigned."""
        source = """add x1, x2, x3
sub x4, x5, x6"""
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert tokens[0].line_num == 1
        assert tokens[4].line_num == 2

    def test_label_tokenization(self):
        """Test that labels are properly tokenized."""
        source = "loop: add x1, x2, x3"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 5
        assert tokens[0].value == "loop:"

    def test_directive_tokenization(self):
        """Test tokenization of directives."""
        source = """.global main
.text
.word 42"""
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert tokens[0].value == ".global"
        assert tokens[1].value == "main"
        assert tokens[2].value == ".text"
        assert tokens[3].value == ".word"
        assert tokens[4].value == "42"

    def test_negative_numbers(self):
        """Test that negative numbers are properly tokenized."""
        source = "addi x1, x2, -42"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert tokens[-1].value == "-42"

    def test_hexadecimal_numbers(self):
        """Test that hexadecimal numbers are properly tokenized."""
        source = "addi x1, x2, 0xFF"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert tokens[-1].value == "0xFF"

    def test_memory_addressing(self):
        """Test tokenization of memory addressing syntax."""
        source = "lw x1, 8(x2)"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert tokens[0].value == "lw"
        assert tokens[1].value == "x1"
        assert tokens[2].value == "8(x2)"

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        source = "  add   x1,  x2,  x3  "
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 4
        assert [t.value for t in tokens] == ["add", "x1", "x2", "x3"]

    def test_token_type(self):
        """Test that tokens have type set."""
        source = "add x1, x2, x3"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        for token in tokens:
            assert token.type == "UNKNOWN"

    def test_only_comments_line(self):
        """Test that lines with only comments are ignored."""
        source = """add x1, x2, x3
# This is a full-line comment
sub x4, x5, x6"""
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert len(tokens) == 8

    def test_mixed_register_names(self):
        """Test tokenization of mixed register names."""
        source = "add ra, x2, sp"
        lexer = Lexer(source)
        tokens = lexer.get_token_stream()
        
        assert tokens[0].value == "add"
        assert tokens[1].value == "ra"
        assert tokens[2].value == "x2"
        assert tokens[3].value == "sp"
