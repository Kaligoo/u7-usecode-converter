# Usecode Parser Design

## Overview

The `usecode_parser.py` module parses Ultima 7's `usecode.dis` disassembly format into structured Python objects for easier analysis and conversion.

## File Format

### Structure
```
.funcnumber 0096H              # Function declaration
.data                          # Data section
L0000: db 'string data'        # String literal
L0038: db 00                   # Null terminator
.code                          # Code section
.argc 0001H                    # Argument count
.localc 0000H                  # Local variable count
.externsize 0002H              # External function count
.extern 08FFH                  # External function reference
0000: 48       push eventid    # Instructions
0001: 1F 01 00 pushi 0001H    ; comment
```

## Data Structures

### UsecodeFunction
Represents a complete function with:
- `func_number`: Function ID (hex)
- `argc`: Number of arguments
- `localc`: Number of local variables
- `data_segments`: List of data labels and strings
- `instructions`: List of bytecode instructions
- `external_funcs`: External function references

### Instruction
Represents a single bytecode instruction:
- `address`: Instruction offset
- `opcode`: Bytecode opcode
- `bytes`: Raw byte array
- `mnemonic`: Assembly mnemonic (push, pushi, callis, etc.)
- `operands`: List of operand strings
- `comment`: Optional comment

### DataSegment
Represents data (strings, bytes):
- `label`: Data label (L0000, L0001, etc.)
- `address`: Offset in data section
- `data`: Actual data (string or bytes)
- `is_string`: True for string data

## Usage

```python
from usecode_parser import parse_usecode_file

# Parse file
functions = parse_usecode_file('usecode.dis')

# Access function
func = functions[0x0096]  # Get function 0x0096
print(f"Function has {func.argc} args, {func.localc} locals")

# Iterate instructions
for inst in func.instructions:
    print(f"{inst.address:04X}: {inst.mnemonic} {inst.operands}")

# Access data
for segment in func.data_segments:
    if segment.is_string:
        print(f"{segment.label}: \"{segment.data}\"")
```

## Key Opcodes

The parser recognizes all usecode opcodes:

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 0x48 | push | Push variable |
| 0x1F | pushi | Push immediate value |
| 0x1D | pushs | Push string |
| 0x38 | callis | Call intrinsic function |
| 0x39 | calli | Call indirect |
| 0x24 | call | Call external function |
| 0x05 | jne | Jump if not equal |
| 0x06 | jmp | Unconditional jump |
| 0x22 | cmpeq | Compare equal |
| 0x25 | ret | Return |
| 0x3E | push objectref | Push object reference |
| 0x10 | not | Logical NOT |

## Parsing Algorithm

1. **Line-by-line parsing** with state tracking
2. **Section detection** (.data, .code, .funcnumber)
3. **Data accumulation** for multi-line strings
4. **Instruction parsing** with regex patterns
5. **Label resolution** for jumps and string references

## Example Output

For function 0x0096 (ship gangplank):

```
Function 0x0096:
  Args: 1 (eventid)
  Locals: 0
  External functions: [0x08FF, 0x0829]

  Data:
    L0000: "@The sails must be furled before the planks are raised.@"
    L0039: "@I think the gangplank is blocked.@"

  Code:
    0000: push eventid
    0001: pushi 0x0001
    0004: cmpeq
    0005: jne 0x0038
    0008: pushi 0x000A
    000B: push objectref
    000C: callis 0x0088, 2  # check_object_flag
    ...
```

## Next Steps

The parsed data structure is ready for the Lua code generator, which will:
1. Convert instructions to Lua statements
2. Resolve data labels to string variables
3. Map intrinsic calls to Lua API functions
4. Generate readable variable names where possible
