from typing import List, Dict, Tuple
import struct
from .lexer import Token 
from .rv32i_isa import RV32I_ISA
from .pseudo import PseudoExpander

class Assembler:
    def __init__(self, token_stream: List[Token], isa: RV32I_ISA):
        self.tokens: List[Token] = token_stream
        self.isa: RV32I_ISA = isa
        self.pseudo = PseudoExpander()
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

    def _get_content_size(self, content: List[Token], current_pc: int) -> int:
        """
        Determines how many bytes a directive or instruction occupies.
        """
        if not content: return 0
        main_token = content[0].value.lower()
        num_args = len(content) - 1

        if main_token == ".word":
            return 4 * num_args
        elif main_token == ".half":
            return 2 * num_args
        elif main_token == ".byte":
            return 1 * num_args
        elif main_token == ".space":
            return int(content[1].value, 0) if num_args >= 1 else 0
        elif main_token == ".align":
            if num_args >= 1:
                power = int(content[1].value, 0)
                alignment = 1 << power
                return (alignment - (current_pc % alignment)) % alignment
            return 0
        elif main_token in [".string", ".asciz", ".ascii"]:
            if num_args >= 1:
                raw_val = content[1].value
                # Ensure we have quotes to strip
                s = raw_val[1:-1] if (len(raw_val) >= 2 and raw_val.startswith('"') and raw_val.endswith('"')) else raw_val
                
                # Decode escape characters
                processed = s.encode('utf-8').decode('unicode_escape').encode('utf-8')
                length = len(processed)
                if main_token != ".ascii":
                    length += 1
                return length
            return 0
        elif main_token.startswith('.'):
            return 0
        elif not main_token.startswith('.'):
            # Check if it is a pseudo instruction
            expanded = self.pseudo.expand(content)
            if expanded:
                return len(expanded) * 4
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

            pc = aligned_pc + self._get_content_size(content, aligned_pc)

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
                # Check for pseudo instruction or standard instruction
                expanded = self.pseudo.expand(content)
                instructions = expanded if expanded else [content]
                
                for instr in instructions:
                    machine_code = self.isa.encode(instr, pc, self.symbol_table)
                    binary_output.extend(struct.pack('<I', machine_code))
                    pc += 4

            elif main_token == ".word":
                for token in content[1:]:
                    val = int(token.value, 0)
                    # Handle signed 32-bit integers by masking
                    if val < 0: val = (1 << 32) + val
                    binary_output.extend(struct.pack('<I', val))
                    pc += 4

            elif main_token == ".half":
                for token in content[1:]:
                    val = int(token.value, 0) & 0xFFFF
                    binary_output.extend(struct.pack('<H', val))
                    pc += 2

            elif main_token == ".byte":
                for token in content[1:]:
                    val = int(token.value, 0) & 0xFF
                    binary_output.append(val)
                    pc += 1
            
            elif main_token == ".space":
                if len(content) > 1:
                    size = int(content[1].value, 0)
                    binary_output.extend(b'\x00' * size)
                    pc += size

            elif main_token == ".align":
                if len(content) > 1:
                    power = int(content[1].value, 0)
                    alignment = 1 << power
                    target = (pc + alignment - 1) & ~(alignment - 1)
                    padding = target - pc
                    binary_output.extend(b'\x00' * padding)
                    pc += padding
            
            elif main_token in [".string", ".asciz", ".ascii"]:
                if len(content) > 1:
                    raw_val = content[1].value
                    s = raw_val[1:-1] if (len(raw_val) >= 2 and raw_val.startswith('"') and raw_val.endswith('"')) else raw_val
                    
                    data = s.encode('utf-8').decode('unicode_escape').encode('utf-8')
                    if main_token != ".ascii":
                        data += b'\x00'
                    
                    binary_output.extend(data)
                    pc += len(data)

        return binary_output