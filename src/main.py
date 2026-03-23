#!/usr/bin/env python3
import argparse
import sys
import os

# Ensure we can import modules from the current directory structure
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assembler.lexer import Lexer
from assembler.rv32i_isa import RV32I_ISA
from assembler.assembler import Assembler

def main():
    parser = argparse.ArgumentParser(description="RISC-V RV32I Assembler")
    parser.add_argument('input_file', help="Path to the input assembly (.asm / .s) file")
    parser.add_argument('-o', '--output', help="Path to the output binary file", default="out.bin")
    parser.add_argument('--h', action='store_true', help="Print output in hexadecimal")
    parser.add_argument('--b', action='store_true', help="Print output in binary")
    parser.add_argument('--print-symbols', action='store_true', help="Print the symbol table after assembly")

    args = parser.parse_args()

    # Minimal fix: prevent conflicting flags
    if args.h and args.b:
        print("Error: Use only one of --h or --b", file=sys.stderr)
        sys.exit(1)

    try:
        # 1. Read Source
        with open(args.input_file, 'r') as f:
            source_code = f.read()

        # 2. Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.get_token_stream()

        # 3. Initialize Components
        isa = RV32I_ISA()
        asm = Assembler(tokens, isa)

        # 4. First Pass (Symbol Resolution)
        asm.first_pass()
        
        if args.print_symbols:
            print("--- Symbol Table ---")
            for label, addr in asm.symbol_table.items():
                print(f"{label}: 0x{addr:08x}")
            print("--------------------")

        # 5. Second Pass (Binary Generation)
        binary = asm.second_pass()

        # 6. Optional formatted output (does NOT affect file writing)
        if args.h:
            print("\n--- HEX OUTPUT ---")
            for i in range(0, len(binary), 4):
                word = binary[i:i+4]
                if len(word) < 4:
                    continue
                print(f"0x{int.from_bytes(word, byteorder='little'):08x}")
            print("------------------")

        if args.b:
            print("\n--- BINARY OUTPUT ---")
            for i in range(0, len(binary), 4):
                word = binary[i:i+4]
                if len(word) < 4:
                    continue
                print(f"{int.from_bytes(word, byteorder='little'):032b}")
            print("---------------------")

        # 7. Write Output
        with open(args.output, 'wb') as f:
            f.write(binary)
        print(f"Assembly successful! Output written to {args.output} ({len(binary)} bytes)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()