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

        # 6. Formatted Output (Memory Dumps)
        if args.h:
            print("\n--- ASSEMBLED MEMORY DUMP (HEX) ---")
            # Step by 16 bytes for a standard hexdump look
            for i in range(0, len(binary), 16):
                chunk = binary[i:i+16]
                # Format each byte as a 2-char hex string
                hex_str = " ".join(f"{b:02x}" for b in chunk)
                print(f"0x{i:08x} |  {hex_str}")
            print("-----------------------------------")

        if args.b:
            print("\n--- ASSEMBLED MEMORY DUMP (BIN) ---")
            # Step by 4 bytes (1 word) to keep lines readable, 
            # but process them byte-by-byte so nothing gets reversed or dropped!
            for i in range(0, len(binary), 4):
                chunk = binary[i:i+4]
                bin_str = " ".join(f"{b:08b}" for b in chunk)
                print(f"0x{i:08x} |  {bin_str}")
            print("-----------------------------------")

        # 7. Write Output
        with open(args.output, 'wb') as f:
            f.write(binary)
        print(f"Assembly successful! Output written to {args.output} ({len(binary)} bytes)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()