from .lexer import Token

class PseudoExpander:
    """
    Translates pseudo-instructions into a list of real instructions (as Token lists).
    """
    
    @staticmethod
    def expand(tokens):
        if not tokens: return None
        
        mnemonic = tokens[0].value.lower()
        args = tokens[1:]
        
        # Helper to create tokens quickly
        def t(val): return Token(str(val), "GENERATED", tokens[0].line_num, 0)
        # Helper to construct a token string like "0(rs1)"
        def t_offset(offset, reg): return Token(f"{offset}({reg.value})", "GENERATED", tokens[0].line_num, 0)
        
        if mnemonic == 'nop':
            # nop -> addi x0, x0, 0
            return [[t("addi"), t("x0"), t("x0"), t("0")]]
            
        elif mnemonic == 'mv':
            # mv rd, rs -> addi rd, rs, 0
            if len(args) == 2:
                return [[t("addi"), args[0], args[1], t("0")]]
        
        elif mnemonic == 'not':
            # not rd, rs -> xori rd, rs, -1
            if len(args) == 2:
                return [[t("xori"), args[0], args[1], t("-1")]]
        
        elif mnemonic == 'neg':
            # neg rd, rs -> sub rd, x0, rs
            if len(args) == 2:
                return [[t("sub"), args[0], t("x0"), args[1]]]

        elif mnemonic == 'ret':
            # ret -> jalr x0, 0(ra)
            return [[t("jalr"), t("x0"), t_offset(0, t("ra"))]]

        elif mnemonic == 'jr':
            # jr rs -> jalr x0, 0(rs)
            if len(args) == 1:
                return [[t("jalr"), t("x0"), t_offset(0, args[0])]]

        elif mnemonic == 'jalr':
            # jalr rs -> jalr x1, 0(rs)
            if len(args) == 1:
                return [[t("jalr"), t("x1"), t_offset(0, args[0])]]

        elif mnemonic == 'j':
            # j label -> jal x0, label
            if len(args) == 1:
                return [[t("jal"), t("x0"), args[0]]]

        elif mnemonic == 'jal':
            # jal label -> jal x1, label
            # (Handles the case where rd is implicit)
            if len(args) == 1:
                return [[t("jal"), t("x1"), args[0]]]

        # --- Branch Pseudos (Zero Comparisons) ---
        elif mnemonic == 'beqz':
            # beqz rs, offset -> beq rs, x0, offset
            if len(args) == 2: return [[t("beq"), args[0], t("x0"), args[1]]]
            
        elif mnemonic == 'bnez':
            # bnez rs, offset -> bne rs, x0, offset
            if len(args) == 2: return [[t("bne"), args[0], t("x0"), args[1]]]
            
        elif mnemonic == 'blez':
            # blez rs, offset -> bge x0, rs, offset
            if len(args) == 2: return [[t("bge"), t("x0"), args[0], args[1]]]
            
        elif mnemonic == 'bgez':
            # bgez rs, offset -> bge rs, x0, offset
            if len(args) == 2: return [[t("bge"), args[0], t("x0"), args[1]]]
            
        elif mnemonic == 'bltz':
            # bltz rs, offset -> blt rs, x0, offset
            if len(args) == 2: return [[t("blt"), args[0], t("x0"), args[1]]]
            
        elif mnemonic == 'bgtz':
            # bgtz rs, offset -> blt x0, rs, offset
            if len(args) == 2: return [[t("blt"), t("x0"), args[0], args[1]]]

        # --- Branch Pseudos (Swapped Operands) ---
        elif mnemonic == 'bgt':
            # bgt rs, rt, offset -> blt rt, rs, offset
            if len(args) == 3: return [[t("blt"), args[1], args[0], args[2]]]
            
        elif mnemonic == 'ble':
            # ble rs, rt, offset -> bge rt, rs, offset
            if len(args) == 3: return [[t("bge"), args[1], args[0], args[2]]]
            
        elif mnemonic == 'bgtu':
            # bgtu rs, rt, offset -> bltu rt, rs, offset
            if len(args) == 3: return [[t("bltu"), args[1], args[0], args[2]]]
            
        elif mnemonic == 'bleu':
            # bleu rs, rt, offset -> bgeu rt, rs, offset
            if len(args) == 3: return [[t("bgeu"), args[1], args[0], args[2]]]

        # --- Set Pseudos ---
        elif mnemonic == 'seqz':
            # seqz rd, rs -> sltiu rd, rs, 1
            if len(args) == 2: return [[t("sltiu"), args[0], args[1], t("1")]]
            
        elif mnemonic == 'snez':
            # snez rd, rs -> sltu rd, x0, rs
            if len(args) == 2: return [[t("sltu"), args[0], t("x0"), args[1]]]
            
        elif mnemonic == 'sltz':
            # sltz rd, rs -> slt rd, rs, x0
            if len(args) == 2: return [[t("slt"), args[0], args[1], t("x0")]]
            
        elif mnemonic == 'sgtz':
            # sgtz rd, rs -> slt rd, x0, rs
            if len(args) == 2: return [[t("slt"), args[0], t("x0"), args[1]]]

        elif mnemonic == 'li':
            # li rd, imm
            # Splits into lui+addi if > 12 bits, or just addi if small
            if len(args) == 2:
                rd = args[0]
                val = int(args[1].value, 0)
                
                if -2048 <= val <= 2047:
                    return [[t("addi"), rd, t("x0"), t(val)]]
                else:
                    # Split into Upper (20 bits) and Lower (12 bits)
                    lower = val & 0xFFF
                    if lower >= 2048: lower -= 4096 # Sign extend adjustment
                    upper = (val - lower) >> 12
                    
                    return [[t("lui"), rd, t(upper)], [t("addi"), rd, rd, t(lower)]]
        
        elif mnemonic == 'la':
            # la rd, symbol -> auipc rd, symbol[31:12]; addi rd, rd, symbol[11:0]
            if len(args) == 2:
                return [
                    [t("auipc"), args[0], t(f"{args[1].value}[31:12]")],
                    [t("addi"), args[0], args[0], t(f"{args[1].value}[11:0]")]
                ]
        
        elif mnemonic in ('lb', 'lh', 'lw'):
            # l{b|h|w} rd, symbol -> auipc rd, symbol[31:12]; l* rd, symbol[11:0](rd)
            if len(args) == 2:
                return [
                    [t("auipc"), args[0], t(f"{args[1].value}[31:12]")],
                    [t(mnemonic), args[0], t(f"{args[1].value}[11:0]({args[0].value})")]
                ]
        
        elif mnemonic in ('sb', 'sh', 'sw'):
            # s{b|h|w} rs, symbol, rt -> auipc rt, symbol[31:12]; s* rs, symbol[11:0](rt)
            if len(args) == 3:
                return [
                    [t("auipc"), args[2], t(f"{args[1].value}[31:12]")],
                    [t(mnemonic), args[0], t(f"{args[1].value}[11:0]({args[2].value})")]
                ]
        
        elif mnemonic == 'call':
            # call offset -> auipc x1, offset[31:12]; jalr x1, offset[11:0](x1)
            if len(args) == 1:
                return [
                    [t("auipc"), t("x1"), t(f"{args[0].value}[31:12]")],
                    [t("jalr"), t("x1"), t(f"{args[0].value}[11:0](x1)")]
                ]
        
        elif mnemonic == 'tail':
            # tail offset -> auipc x6, offset[31:12]; jalr x0, offset[11:0](x6)
            if len(args) == 1:
                return [
                    [t("auipc"), t("x6"), t(f"{args[0].value}[31:12]")],
                    [t("jalr"), t("x0"), t(f"{args[0].value}[11:0](x6)")]
                ]
        
        elif mnemonic == 'fence':
            # fence -> fence iorw, iorw
            return [[t("fence"), t("iorw"), t("iorw")]]
        
        return None