# Use Alpine Edge for the most up-to-date RISC-V tools
FROM alpine:edge

# Install Python and RISC-V binary utilities
RUN apk add --no-cache \
    python3 \
    py3-pip \
    binutils-riscv-none-elf \
    make

# Set up a working directory
WORKDIR /app

# Copy your Python requirements
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy your assembler source code
COPY . .

# Default command: run your assembler script
# Assuming your main script is called 'assembler.py'
CMD ["python3", "src/main.py"]