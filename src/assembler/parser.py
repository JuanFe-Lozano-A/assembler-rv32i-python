from typing import List, Dict, Tuple
import struct
from .lexer import Token 
from .rv32i_isa import RV32I_ISA

class Parser:
    def __init__(self, token_stream: List[Token], isa: RV32I_ISA):
        self.tokens: List[Token] = token_stream
        self.isa: RV32I_ISA = isa
        self.symbol_table: Dict[str, int] = {}

    def _group_by_line(self) -> List[List[Token]]:
        """
        Groups the flat token stream into lists by line number.
        """
        lines: Dict[int, List[Token]] = {}
        for token in self.tokens:
            if token.line_num not in lines:
                lines[token.line_num] = []
            lines[token.line_num].append(token)
        return list(lines.values())
    
    def _check_if_instruction(self, line: List[Token]) -> bool:
        """
        Returns True if the line contains a RISC-V instruction.
        """
        if not line: return False
        first_token = line[0]
        if first_token.value.endswith(':'):
            return len(line) > 1 and not line[1].value.startswith('.')
        return not first_token.value.startswith('.')

    def _get_line_details(self, line: List[Token], pc: int) -> Tuple[int, List[Token]]:
        """
        Unifies alignment logic and label stripping for both passes.
        """
        # 1. Alignment check
        if self._check_if_instruction(line):
            pc = (pc + 3) & ~3
        
        # 2. Extract content (strip label if present)
        content = line[1:] if line[0].value.endswith(':') else line
        return pc, content

    def _get_content_size(self, content: List[Token]) -> int:
        """
        Determines how many bytes a directive or instruction occupies.
        """
        if not content: return 0
        main_token = content[0].value.lower()
        if main_token == ".word":
            return 4
        elif main_token == ".byte":
            return 1
        elif main_token in [".section", ".global", ".text", ".data"]:
            return 0
        elif not main_token.startswith('.'):
            return 4
        return 0

    def first_pass(self) -> None:
        """
        Records label addresses into the symbol table.
        """
        pc = 0
        for line in self._group_by_line():
            if not line: continue
            
            aligned_pc, content = self._get_line_details(line, pc)

            # Record label at the aligned PC
            if line[0].value.endswith(':'):
                label_name = line[0].value[:-1]
                self.symbol_table[label_name] = aligned_pc

            pc = aligned_pc + self._get_content_size(content)

    def second_pass(self) -> bytearray:
        """
        Generates the actual binary using the symbol table.
        """
        pc = 0
        binary_output = bytearray()

        for line in self._group_by_line():
            if not line: continue

            aligned_pc, content = self._get_line_details(line, pc)

            while pc < aligned_pc:
                binary_output.append(0)
                pc += 1

            if not content: continue
            main_token = content[0].value.lower()

            if not main_token.startswith('.'):
                machine_code = self.isa.encode(content, pc, self.symbol_table)
                binary_output.extend(struct.pack('<I', machine_code))
                pc += 4

            elif main_token == ".word":
                val = int(content[1].value, 0)
                binary_output.extend(struct.pack('<I', val))
                pc += 4

            elif main_token == ".byte":
                val = int(content[1].value, 0) & 0xFF
                binary_output.append(val)
                pc += 1

        return binary_output