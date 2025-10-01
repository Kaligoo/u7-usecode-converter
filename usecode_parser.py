"""
Usecode Parser for Ultima 7

Parses the usecode.dis disassembly format into structured Python data.

Format:
    .funcnumber 0096H
    .data
    L0000: db 'string data'
    .code
    .argc 0001H
    .localc 0000H
    0000: 48    push eventid
    0001: 1F 01 00    pushi 0001H
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union


@dataclass
class DataSegment:
    """Represents a data label and its content."""
    label: str
    address: int
    data: Union[str, bytes]
    is_string: bool


@dataclass
class Instruction:
    """Represents a single usecode instruction."""
    address: int
    opcode: int
    bytes: List[int]
    mnemonic: str
    operands: List[str]
    comment: Optional[str] = None


@dataclass
class UsecodeFunction:
    """Represents a complete usecode function."""
    func_number: int
    argc: int = 0
    localc: int = 0
    data_segments: List[DataSegment] = field(default_factory=list)
    data_labels: Dict[str, DataSegment] = field(default_factory=dict)
    instructions: List[Instruction] = field(default_factory=list)
    external_funcs: List[int] = field(default_factory=list)
    externsize: int = 0


class UsecodeParser:
    """Parser for usecode.dis format."""

    def __init__(self):
        self.functions: Dict[int, UsecodeFunction] = {}
        self.current_function: Optional[UsecodeFunction] = None
        self.in_data_section = False
        self.in_code_section = False

    def parse_file(self, filepath: str) -> Dict[int, UsecodeFunction]:
        """Parse a usecode.dis file and return all functions."""
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                self.parse_line(line.rstrip())

        return self.functions

    def parse_line(self, line: str):
        """Parse a single line from usecode.dis."""
        # Skip empty lines and pure whitespace
        if not line.strip():
            return

        # Function number
        if '.funcnumber' in line:
            match = re.search(r'\.funcnumber\s+([0-9A-F]+)H', line)
            if match:
                func_num = int(match.group(1), 16)
                self.current_function = UsecodeFunction(func_number=func_num)
                self.functions[func_num] = self.current_function
                self.in_data_section = False
                self.in_code_section = False
                return

        if not self.current_function:
            return

        # Section markers
        if '.data' in line:
            self.in_data_section = True
            self.in_code_section = False
            return

        if '.code' in line:
            self.in_data_section = False
            self.in_code_section = True
            return

        # Function metadata
        if '.argc' in line:
            match = re.search(r'\.argc\s+([0-9A-F]+)H', line)
            if match:
                self.current_function.argc = int(match.group(1), 16)
            return

        if '.localc' in line:
            match = re.search(r'\.localc\s+([0-9A-F]+)H', line)
            if match:
                self.current_function.localc = int(match.group(1), 16)
            return

        if '.externsize' in line:
            match = re.search(r'\.externsize\s+([0-9A-F]+)H', line)
            if match:
                self.current_function.externsize = int(match.group(1), 16)
            return

        if '.extern' in line:
            match = re.search(r'\.extern\s+([0-9A-F]+)H', line)
            if match:
                self.current_function.external_funcs.append(int(match.group(1), 16))
            return

        # Data section
        if self.in_data_section:
            self._parse_data_line(line)
            return

        # Code section
        if self.in_code_section:
            self._parse_code_line(line)
            return

    def _parse_data_line(self, line: str):
        """Parse a data segment line."""
        # Format: L0000: db 'string' or L0000: db 00
        match = re.match(r'(L[0-9A-F]+):\s+db\s+(.+)', line)
        if not match:
            # Continuation line (multi-line strings)
            if line.strip().startswith('db'):
                # Handle continuation
                match = re.match(r'\s+db\s+(.+)', line)
                if match and self.current_function.data_segments:
                    # Append to last data segment
                    last_seg = self.current_function.data_segments[-1]
                    if last_seg.is_string:
                        content = match.group(1).strip()
                        if content.startswith("'") and content.endswith("'"):
                            content = content[1:-1]
                        last_seg.data += content
            return

        label = match.group(1)
        content = match.group(2).strip()

        # Parse address from label
        addr = int(label[1:], 16)

        # Determine if string or byte
        is_string = False
        data = None

        if content.startswith("'") and content.endswith("'"):
            # String data
            is_string = True
            data = content[1:-1]  # Remove quotes
        else:
            # Byte data (usually 00 for null terminator)
            try:
                data = int(content, 16)
            except ValueError:
                data = content

        segment = DataSegment(
            label=label,
            address=addr,
            data=data,
            is_string=is_string
        )

        self.current_function.data_segments.append(segment)
        self.current_function.data_labels[label] = segment

    def _parse_code_line(self, line: str):
        """Parse a code instruction line."""
        # Format: 0000: 48    push eventid    ; comment
        match = re.match(r'([0-9A-F]+):\s+([0-9A-F ]+)\s+(\w+)(?:\s+(.+?))?(?:\s*;\s*(.+))?$', line)
        if not match:
            return

        addr = int(match.group(1), 16)
        byte_str = match.group(2).strip()
        mnemonic = match.group(3)
        operands_str = match.group(4) or ''
        comment = match.group(5)

        # Parse bytes
        bytes_list = [int(b, 16) for b in byte_str.split()]
        opcode = bytes_list[0] if bytes_list else 0

        # Parse operands
        operands = []
        if operands_str:
            # Split by comma, but be careful with brackets
            operands = [op.strip() for op in operands_str.split(',')]

        instruction = Instruction(
            address=addr,
            opcode=opcode,
            bytes=bytes_list,
            mnemonic=mnemonic,
            operands=operands,
            comment=comment
        )

        self.current_function.instructions.append(instruction)


def parse_usecode_file(filepath: str) -> Dict[int, UsecodeFunction]:
    """Convenience function to parse a usecode.dis file."""
    parser = UsecodeParser()
    return parser.parse_file(filepath)


if __name__ == '__main__':
    # Test parser
    import sys

    if len(sys.argv) < 2:
        print("Usage: python usecode_parser.py <usecode.dis>")
        sys.exit(1)

    functions = parse_usecode_file(sys.argv[1])

    print(f"Parsed {len(functions)} functions")

    # Show first function details
    if functions:
        first_func = list(functions.values())[0]
        print(f"\nFunction 0x{first_func.func_number:04X}:")
        print(f"  Args: {first_func.argc}")
        print(f"  Locals: {first_func.localc}")
        print(f"  Data segments: {len(first_func.data_segments)}")
        print(f"  Instructions: {len(first_func.instructions)}")

        if first_func.data_segments:
            print(f"\n  First data segment:")
            seg = first_func.data_segments[0]
            print(f"    {seg.label}: {seg.data[:50]}..." if len(str(seg.data)) > 50 else f"    {seg.label}: {seg.data}")

        if first_func.instructions:
            print(f"\n  First 5 instructions:")
            for inst in first_func.instructions[:5]:
                ops = ', '.join(inst.operands) if inst.operands else ''
                print(f"    {inst.address:04X}: {inst.mnemonic:10s} {ops}")
