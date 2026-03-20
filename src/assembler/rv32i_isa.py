class RV32I_ISA:
    def __init__(self):
    # Instructions mapped to (Opcode, Func3, Func7, FormatType)
    # None is used where a field doesn't exist for that format
        self.INSTRUCTIONS = {
            # R type formats
            "add": (0x33, 0x0, 0x00, "R"),
            "sub": (0x33, 0x0, 0x20, "R"),
            "xor": (0x33, 0x4, 0x00, "R"),
            "or": (0x33, 0x6, 0x00, "R"),
            "and": (0x33, 0x7, 0x00, "R"),
            "sll": (0x33, 0x1, 0x00, "R"),
            "srl": (0x33, 0x5, 0x00, "R"),
            "sra": (0x33, 0x5, 0x20, "R"),
            "slt": (0x33, 0x2, 0x00, "R"),
            "sltu": (0x33, 0x3, 0x00, "R"),
            # I type formats
            "addi": (0x13, 0x0, None, "I"),
            "xori": (0x13, 0x4, None, "I"),
            "ori": (0x13, 0x6, None, "I"),
            "andi": (0x13, 0x7, None, "I"),
            "slli": (0x13, 0x1, 0x00, "I"),
            "srli": (0x13, 0x5, 0x00, "I"),
            "srai": (0x13, 0x5, 0x20, "I"),
            "slti": (0x13, 0x2, None, "I"),
            "sltiu": (0x13, 0x3, None, "I"),
            # I type byte handling formats
            "lb": (0x03, 0x0, None, "I"),
            "lh": (0x03, 0x1, None, "I"),
            "lw": (0x03, 0x2, None, "I"),
            "lbu": (0x03, 0x4, None, "I"),
            "lhu": (0x03, 0x5, None, "I"),
            # S type formats
            "sb": (0x23, 0x0, None, "S"),
            "sh": (0x23, 0x1, None, "S"),
            "sw": (0x23, 0x2, None, "S"),
            # B type formats
            "beq": (0x63, 0x0, None, "B"),
            "bne": (0x63, 0x1, None, "B"),
            "blt": (0x63, 0x4, None, "B"),
            "bge": (0x63, 0x5, None, "B"),
            "bltu": (0x63, 0x6, None, "B"),
            "bgeu": (0x63, 0x7, None, "B"),
            # J and I jump type formats
            "jal": (0x6f, None, None, "J"),
            "jalr": (0x67, 0x0, None, "I"),
            # U type formats
            "lui": (0x37, None, None, "U"),
            "auipc": (0x17, None, None, "U"),
            # I environment type formats
            "ecall": (0x73, 0x0, 0x0, "I"),
            "ebrake": (0x73, 0x0, 0x1, "I")
        }

        self.REGISTERS = {
            # Zero constant register
            "zero": 0,
            # Special registers (return address, stack pointer, global pointer, thread pointer)
            "ra": 1, "sp": 2, "gp": 3, "tp": 4,
            # T registers
            "t0": 5, "t1": 6, "t2": 7,
            # Special x8 name
            "fp": 8,
            # Saved registers
            "s0": 8,
            "s1": 9,
            # Fn argument registers (return values)
            "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17,
            # Saved registers
            "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22,
            "s7": 23, "s8": 24, "s9": 25, "s10": 26, "s11": 27,
            # Temporary registers
            "t3": 28, "t4": 29, "t5": 30, "t6": 31
        }
        
        # Automatically add x0 through x31 to the dictionary
        for i in range(32):
            self.REGISTERS[f"x{i}"] = i

    def get_info(self, mnemonic):
        """
        Returns (opcode, f3, f7, fmt) or raises error.
        """
        if mnemonic not in self.INSTRUCTIONS:
            raise ValueError(f"Unknown instruction: {mnemonic}")
        return self.INSTRUCTIONS[mnemonic]
    
    def get_reg(self, reg_name):
        """
        Translates 'ra' or 'x1' to 1.
        """
        val = self.REGISTERS.get(reg_name)
        if val is None:
            raise ValueError(f"Invalid register: {reg_name}")
        return val

    def _parse_mem(self, arg):
        """Parses 'offset(base)' or just returns (0, base) or (imm, zero)."""
        if '(' in arg and arg.endswith(')'):
            offset_str, base_str = arg[:-1].split('(')
            return int(offset_str, 0), self.get_reg(base_str)
        raise ValueError(f"Expected memory address 'offset(base)', got {arg}")

    def encode(self, tokens: list, current_pc: int, symbol_table: dict) -> int:
        """
        The Dispatcher: Translates tokens into a 32-bit machine code word.
        """
        mnemonic = tokens[0].value.lower()
        opcode, f3, f7, fmt = self.get_info(mnemonic)

        args = [t.value for t in tokens[1:]]

        if fmt == "R":
            return self._pack_r(opcode, f3, f7, args)
        elif fmt == "I":
            return self._pack_i(opcode, f3, f7, args)
        elif fmt == "S":
            return self._pack_s(opcode, f3, args)
        elif fmt == "B":
            target_addr = symbol_table.get(args[-1])
            if target_addr is None: raise ValueError(f"Label {args[-1]} not found")
            offset = target_addr - current_pc
            return self._pack_b(opcode, f3, args, offset)
        elif fmt == "U":
            return self._pack_u(opcode, args)
        elif fmt == "J":
            target_addr = symbol_table.get(args[-1])
            if target_addr is None: raise ValueError(f"Label {args[-1]} not found")
            offset = target_addr - current_pc
            return self._pack_j(opcode, args, offset)
        return 0

    def _pack_r(self, opcode, f3, f7, args):
        # rd, rs1, rs2
        rd = self.get_reg(args[0])
        rs1 = self.get_reg(args[1])
        rs2 = self.get_reg(args[2])
        return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | opcode

    def _pack_i(self, opcode, f3, f7, args):
        # Formats: "addi rd, rs1, imm", "lw rd, off(rs1)", or "ecall" (no args)
        if not args: # ecall, ebreak
            return (0 << 20) | (0 << 15) | (f3 << 12) | (0 << 7) | opcode

        rd = self.get_reg(args[0])
        
        # Load instructions or explicit offset syntax
        if len(args) == 2: 
            imm, rs1 = self._parse_mem(args[1])
        else: # Arithmetic: addi rd, rs1, imm
            rs1 = self.get_reg(args[1])
            imm = int(args[2], 0)

        # Special handling for shifts (slli, etc) where f7 holds the top bits
        if f7 is not None:
            imm = (f7 << 5) | (imm & 0x1F)
        
        return ((imm & 0xFFF) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | opcode

    def _pack_s(self, opcode, f3, args):
        # sw rs2, offset(rs1)
        rs2 = self.get_reg(args[0])
        imm, rs1 = self._parse_mem(args[1])
        
        imm11_5 = (imm >> 5) & 0x7F
        imm4_0 = imm & 0x1F
        return (imm11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (imm4_0 << 7) | opcode

    def _pack_b(self, opcode, f3, args, offset):
        # beq rs1, rs2, label
        rs1 = self.get_reg(args[0])
        rs2 = self.get_reg(args[1])
        
        imm = offset >> 1 # B-type ignores bit 0
        imm_12 = (imm >> 11) & 1
        imm_10_5 = (imm >> 4) & 0x3F
        imm_4_1 = imm & 0xF
        imm_11 = (imm >> 10) & 1
        
        encoded_imm = (imm_12 << 31) | (imm_10_5 << 25) | (imm_4_1 << 8) | (imm_11 << 7)
        return encoded_imm | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | opcode

    def _pack_u(self, opcode, args):
        # lui rd, imm
        rd = self.get_reg(args[0])
        imm = int(args[1], 0)
        return ((imm & 0xFFFFF) << 12) | (rd << 7) | opcode

    def _pack_j(self, opcode, args, offset):
        # jal rd, label
        rd = self.get_reg(args[0])
        
        imm = offset >> 1
        imm_20 = (imm >> 19) & 1
        imm_10_1 = imm & 0x3FF
        imm_11 = (imm >> 10) & 1
        imm_19_12 = (imm >> 11) & 0xFF
        
        encoded_imm = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12)
        return encoded_imm | (rd << 7) | opcode