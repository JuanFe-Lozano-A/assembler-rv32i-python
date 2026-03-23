FROM python:3.13.1-slim

# Install RISC-V binary utilities (Debian package name for binutils-riscv-none-elf)
RUN apt-get update && apt-get install -y \
    binutils-riscv64-unknown-elf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt

CMD ["/bin/bash"]