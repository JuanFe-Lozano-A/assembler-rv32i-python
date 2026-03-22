# RISC-V RV32I Assembler

A Python implementation of a RISC-V RV32I assembler that translates assembly code into machine code binary files.

## Overview

This project is a complete assembler for the RISC-V RV32I instruction set. It takes assembly source files (`.s` or `.asm`) and produces binary executable files that can run on RISC-V processors or simulators.

### Features

- **Full RV32I ISA Support**: Encodes all base integer instructions (R, I, S, B, U, J formats)
- **Pseudo-Instruction Expansion**: Automatically expands common pseudo-instructions like `mv`, `li`, `la`, `call`, `tail`, and conditional branches
- **Symbol Resolution**: Two-pass assembly with label resolution and symbol table management
- **Directive Support**: Handles directives like `.word`, `.byte`, `.half`, `.string`, `.asciz`, `.ascii`, `.space`, `.align`, `.global`, `.text`, and `.section`
- **Flexible Syntax**: Supports both x-register names (x0-x31) and ABI names (ra, sp, gp, etc.)
- **Error Handling**: Provides meaningful error messages for invalid instructions and unresolved symbols

### Architecture

The assembler consists of several key components:

- **Lexer** (`lexer.py`): Tokenizes input assembly source code
- **ISA** (`rv32i_isa.py`): Manages instruction definitions and encoding for the RV32I instruction set
- **Pseudo Expander** (`pseudo.py`): Expands pseudo-instructions into base instructions
- **Assembler** (`assembler.py`): Main two-pass assembler that performs symbol resolution and binary generation

## Setup

### Prerequisites

- Python 3.14.3 or higher
- pip (Python package manager)
- `binutils-riscv-none-elf` (for local development)

### Local Installation

This project requires Python 3.14.3. The `.python-version` file is provided for use with tools like `pyenv`.

It also requires `binutils-riscv-none-elf` to be installed and in your `PATH`. This provides the necessary tools for working with RISC-V binaries. Please install it using your system's package manager.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JuanFe-Lozano-A/assembler-rv32i-python.git
   cd assembler-rv32i-python
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies** (for testing):
   ```bash
   pip install -r requirements-dev.txt
   ```

## Running the Assembler

### Command-Line Interface

Assemble an assembly file using the CLI:

```bash
python3 src/main.py <input_file> -o <output_file>
```

**Options**:
- `<input_file>`: Path to the input assembly file (`.s` or `.asm`)
- `-o, --output`: Path to the output binary file (default: `out.bin`)
- `--print-symbols`: Print the symbol table after assembly

**Example**:
```bash
python3 src/main.py program.s -o program.bin --print-symbols
```

This will:
1. Read the assembly source from `program.s`
2. Generate a binary file `program.bin`
3. Print all resolved symbol addresses

### Sample Assembly Program

Create a file named `hello.s`:

```asm
.global main
.text

main:
  addi x1, x0, 5
  addi x2, x0, 10
  add x3, x1, x2
  jal x0, main
```

Assemble it:
```bash
python3 src/main.py hello.s -o hello.bin
```

## Testing

The project includes a comprehensive test suite with 108 tests covering:
- Lexical analysis
- Instruction encoding for all instruction types
- Pseudo-instruction expansion
- Symbol resolution
- Assembler directives
- Integration tests for complete assembly

### Running Tests

Activate the virtual environment and run tests:

```bash
source .venv/bin/activate  # On macOS/Linux
python3 -m pytest tests/ -v
```

**Test Coverage**:
- `tests/test_lexer.py`: 15 tests for tokenization
- `tests/test_isa.py`: 25 tests for ISA encoding
- `tests/test_pseudo.py`: 31 tests for pseudo-instruction expansion
- `tests/test_assembler.py`: 28 integration tests
- `tests/test_directives.py`: 9 tests for assembler directives

All tests should pass:
```
============================== 108 passed in 0.05s ==============================
```

## Requirements

### Core Dependencies

- `bitstring>=4.0.0`: Bit manipulation utilities
- `click>=8.0.0`: CLI framework (may be extended in future versions)

### Development Dependencies

- `pytest>=7.0.0`: Testing framework
- `black>=23.0.0`: Code formatter
- `pylint>=2.0.0`: Code linter

See `requirements.txt` and `requirements-dev.txt` for complete dependency lists.

## Docker Setup

The project includes Docker configuration for isolated development and testing environments.

### Prerequisites

- Docker
- Docker Compose

### Building the Docker Image

```bash
docker-compose build
```

### Running in Docker

Start the container:
```bash
docker-compose up -d
```

Access the container:
```bash
docker exec -it riscv_dev /bin/sh
```

### Running the Assembler in Docker

Once inside the container:

```bash
python3 src/main.py /app/program.s -o /app/program.bin
```

### Running Tests in Docker

```bash
docker-compose exec riscv_dev python3 -m pytest tests/ -v
```

### Dockerfile Details

The `dockerfile` uses Alpine Linux with:
- Python 3.x
- RISC-V binary utilities
- All project dependencies (core and development)

### Docker Compose Configuration

The `docker-compose.yaml` sets up:
- Container name: `riscv_dev`
- Working directory: `/app`
- Volume mount: Current directory to `/app`
- Python environment flag: `PYTHONDONTWRITEBYTECODE=1`

This ensures that:
- Your local code is synced with the container
- Changes made locally are immediately reflected in the container
- Python bytecode files are not generated, keeping the container clean

## Instruction Reference

### Supported Instruction Types

| Format | Examples | Count |
|--------|----------|-------|
| R-Type | add, sub, xor, or, and, sll, srl, sra, slt, sltu | 10 |
| I-Type | addi, xori, ori, andi, slli, srli, srai, slti, sltiu | 9 |
| Load | lb, lh, lw, lbu, lhu | 5 |
| S-Type | sb, sh, sw | 3 |
| B-Type | beq, bne, blt, bge, bltu, bgeu | 6 |
| U-Type | lui, auipc | 2 |
| J-Type | jal | 1 |
| Environment | ecall, ebreak | 2 |

### Supported Pseudo-Instructions

Common pseudo-instructions are automatically expanded:
- `nop`, `mv`, `not`, `neg`
- `j`, `jal`, `jr`, `ret`, `call`, `tail`
- `beqz`, `bnez`, `bgez`, `bltz`, `bgtz`, `blez`
- `bgt`, `ble`, `bgtu`, `bleu`
- `seqz`, `snez`, `sltz`, `sgtz`
- `li`, `la`, `fence`
- Load/store with symbols: `lb`, `lh`, `lw`, `sb`, `sh`, `sw`

## Project Structure

```
assembler-rv32i-python/
├── src/
│   ├── main.py                 # CLI entry point
│   └── assembler/
│       ├── __init__.py         # Package initialization
│       ├── lexer.py            # Tokenizer
│       ├── rv32i_isa.py        # ISA definitions and encoding
│       ├── pseudo.py           # Pseudo-instruction expansion
│       └── assembler.py        # Main assembler logic
├── tests/
│   ├── test_lexer.py           # Lexer tests
│   ├── test_isa.py             # ISA encoding tests
│   ├── test_pseudo.py          # Pseudo-instruction tests
│   ├── test_assembler.py       # Integration tests
│   └── test_directives.py      # Directive tests
├── dockerfile                   # Docker container definition
├── docker-compose.yaml         # Docker Compose configuration
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

## Future Enhancements

- **UI-Based Assembler Interface**: Develop a simple web-based UI (e.g., using Flask or FastAPI with a simple frontend) to allow users to write and assemble code without using the CLI.
- **Disassembler Functionality**: Implement a disassembler to convert machine code back into human-readable assembly, aiding in debugging and analysis.
- **Debugging Features**: Add features to the assembler or a companion tool to support debugging, such as setting breakpoints, inspecting registers, and stepping through code.
- **Extended Instruction Set Support**: Expand the assembler to support other RISC-V extensions, such as the 64-bit integer instruction set (RV64I) or floating-point extensions (F, D).
- **Macro Support**: Implement support for user-defined macros to simplify complex or repetitive code patterns.
- **Code validation and linting**: Add more robust validation and linting of the assembly code to catch common errors and enforce coding standards.

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests:

```bash
python3 -m pytest tests/ -v
python3 -m black src/ tests/
python3 -m pylint src/
```
