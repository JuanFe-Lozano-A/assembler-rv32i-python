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
        """Returns (opcode, f3, f7, fmt) or raises error."""
        if mnemonic not in self.INSTRUCTIONS:
            raise ValueError(f"Unknown instruction: {mnemonic}")
        return self.INSTRUCTIONS[mnemonic]
    
    def get_reg(self, reg_name):
        """Translates 'ra' or 'x1' to 1."""
        val = self.REGISTERS.get(reg_name)
        if val is None:
            raise ValueError(f"Invalid register: {reg_name}")
        return val