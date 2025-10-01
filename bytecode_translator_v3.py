"""
Bytecode to Lua Translator V3

Fixed version with proper sequential instruction processing and correct control flow.
"""

from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass
from usecode_parser import UsecodeFunction, Instruction
from intrinsic_mapping import INTRINSIC_MAP


@dataclass
class StackValue:
    """Represents a value on the simulated stack."""
    expr: str  # The Lua expression


class BytecodeTranslator:
    """Translates usecode bytecode to Lua."""

    def __init__(self, func: UsecodeFunction):
        self.func = func
        self.stack: List[StackValue] = []
        self.lines: List[str] = []
        self.indent_level = 1
        self.indent_str = "    "
        self.pc = 0  # Program counter
        self.inst_map: Dict[int, int] = {}  # Address -> instruction index
        self.jump_targets: Set[int] = set()

        # Build instruction address map
        for i, inst in enumerate(func.instructions):
            self.inst_map[inst.address] = i

        # Find all jump targets
        for inst in func.instructions:
            if inst.mnemonic in ['jmp', 'jne', 'je'] and inst.operands:
                target = int(inst.operands[0], 16)
                self.jump_targets.add(target)

    def translate(self) -> List[str]:
        """Main translation entry point."""
        self.lines = []
        self.pc = 0
        self.stack = []

        while self.pc < len(self.func.instructions):
            inst = self.func.instructions[self.pc]

            # Try to match if-statement pattern
            if self._try_translate_if():
                continue

            # Translate single instruction
            line = self._translate_instruction(inst)
            if line:
                self.lines.append(self._indent(line))

            self.pc += 1

        return self.lines

    def _try_translate_if(self) -> bool:
        """Try to translate if-statement pattern."""
        # Look for: push, push/pushi, cmpeq/cmpne/etc, jne/je
        # This is the pattern: condition comparison followed by conditional jump

        if self.pc + 3 >= len(self.func.instructions):
            return False

        # Look ahead to find comparison + jump pattern
        # We need to be more careful: only look at the immediate next few instructions
        cmp_idx = -1
        jump_idx = -1

        # Scan up to 4 instructions ahead for comparison (not 5!)
        # AND only if we see consecutive stack-building operations
        for offset in range(min(4, len(self.func.instructions) - self.pc)):
            inst = self.func.instructions[self.pc + offset]

            # If we hit a pop before finding comparison, this isn't an if pattern
            if inst.mnemonic == 'pop':
                return False

            if inst.mnemonic in ['cmpeq', 'cmpne', 'cmplt', 'cmple', 'cmpgt', 'cmpge']:
                cmp_idx = self.pc + offset
                # Check if next instruction is a conditional jump
                if offset + 1 < len(self.func.instructions) - self.pc:
                    next_inst = self.func.instructions[self.pc + offset + 1]
                    if next_inst.mnemonic in ['jne', 'je']:
                        jump_idx = self.pc + offset + 1
                        break

        if cmp_idx == -1 or jump_idx == -1:
            return False

        cmp_inst = self.func.instructions[cmp_idx]
        jump_inst = self.func.instructions[jump_idx]

        # Count how many stack operations we need before the comparison
        # Comparison needs exactly 2 values on the stack
        stack_ops_needed = 2

        # Find instructions that build the stack for comparison
        # These should be push/pushi instructions right before the comparison
        stack_builder_start = cmp_idx - 1
        stack_values_found = 0

        while stack_builder_start >= self.pc and stack_values_found < stack_ops_needed:
            inst = self.func.instructions[stack_builder_start]
            if inst.mnemonic in ['push', 'pushi', 'pushs']:
                stack_values_found += 1
                stack_builder_start -= 1
            else:
                break

        stack_builder_start += 1  # Adjust back to first stack op

        # Output any instructions BEFORE the stack builders as regular statements
        while self.pc < stack_builder_start:
            inst = self.func.instructions[self.pc]
            line = self._translate_instruction(inst)
            if line:
                self.lines.append(self._indent(line))
            self.pc += 1

        # Now process the stack operations for the comparison
        temp_stack = []
        for idx in range(stack_builder_start, cmp_idx):
            inst = self.func.instructions[idx]
            self._process_stack_op_to_list(inst, temp_stack)

        # Build comparison expression
        if len(temp_stack) >= 2:
            right = temp_stack.pop()
            left = temp_stack.pop()

            op_map = {
                'cmpeq': '==', 'cmpne': '~=',
                'cmplt': '<', 'cmple': '<=',
                'cmpgt': '>', 'cmpge': '>='
            }
            op = op_map.get(cmp_inst.mnemonic, '==')

            # Handle jump semantics
            # jne = jump if NOT equal (i.e., jump if false), so we want: if (condition)
            if jump_inst.mnemonic == 'jne':
                condition = f"{left.expr} {op} {right.expr}"
            else:  # je = jump if equal (i.e., jump if true), so invert
                inv_op = {'==': '~=', '~=': '==', '<': '>=', '>=': '<', '>': '<=', '<=': '>'}
                op = inv_op.get(op, op)
                condition = f"{left.expr} {op} {right.expr}"

            # Output the if statement
            self.lines.append(self._indent(f"if {condition} then"))
            self.indent_level += 1

            # Get jump target - this is where we go if condition is FALSE
            target_addr = int(jump_inst.operands[0], 16)

            # Move PC past the comparison and jump
            self.pc = jump_idx + 1

            # Translate the "then" body (instructions until we reach the jump target)
            # The jump target is where we go if the condition is FALSE
            # So we process instructions UP TO (but not including) the target
            while self.pc < len(self.func.instructions):
                inst = self.func.instructions[self.pc]

                # Stop if we've reached THIS if's jump target (where FALSE condition lands)
                if inst.address >= target_addr:
                    # PC is now AT the target - don't advance it
                    break

                # Try to handle nested if first
                if self._try_translate_if():
                    # _try_translate_if advanced PC, continue loop
                    continue

                # Translate single instruction
                line = self._translate_instruction(inst)
                if line:
                    self.lines.append(self._indent(line))

                self.pc += 1

            self.indent_level -= 1
            self.lines.append(self._indent("end"))

            # IMPORTANT: PC is now at the jump target address
            # The main loop will continue from here, potentially finding another if
            # This creates sequential if statements at the same level
            return True

        # If we couldn't match the pattern, don't consume anything
        return False

    def _process_stack_op_to_list(self, inst: Instruction, stack: List[StackValue]):
        """Process instruction that manipulates a separate stack list."""
        if inst.mnemonic == 'push':
            var_name = inst.operands[0] if inst.operands else 'unknown'
            var_name = self._convert_var_name(var_name)
            stack.append(StackValue(var_name))

        elif inst.mnemonic == 'pushi':
            value = inst.operands[0] if inst.operands else '0'
            if 'H' in value:
                value = str(int(value.replace('H', ''), 16))
            stack.append(StackValue(value))

        elif inst.mnemonic == 'pushs':
            label = inst.operands[0] if inst.operands else 'L0000'
            stack.append(StackValue(f"str_{label}"))

    def _translate_instruction(self, inst: Instruction) -> Optional[str]:
        """Translate a single instruction to Lua."""

        # Stack operations
        if inst.mnemonic == 'push':
            var_name = inst.operands[0] if inst.operands else 'unknown'
            var_name = self._convert_var_name(var_name)
            self.stack.append(StackValue(var_name))
            return None

        elif inst.mnemonic == 'pushi':
            value = inst.operands[0] if inst.operands else '0'
            if 'H' in value:
                value = str(int(value.replace('H', ''), 16))
            self.stack.append(StackValue(value))
            return None

        elif inst.mnemonic == 'pushs':
            label = inst.operands[0] if inst.operands else 'L0000'
            self.stack.append(StackValue(f"str_{label}"))
            return None

        elif inst.mnemonic == 'pop':
            if self.stack and inst.operands:
                value = self.stack.pop()
                var_name = self._convert_var_name(inst.operands[0])
                return f"{var_name} = {value.expr}"
            return None

        # Function calls
        elif inst.mnemonic == 'callis':
            return self._translate_callis(inst)

        elif inst.mnemonic == 'calli':
            return self._translate_calli(inst)

        # Arithmetic
        elif inst.mnemonic in ['add', 'sub', 'mul', 'div', 'mod']:
            if len(self.stack) >= 2:
                right = self.stack.pop()
                left = self.stack.pop()
                op_map = {'add': '+', 'sub': '-', 'mul': '*', 'div': '//', 'mod': '%'}
                self.stack.append(StackValue(f"({left.expr} {op_map[inst.mnemonic]} {right.expr})"))
            return None

        # Logical
        elif inst.mnemonic == 'not':
            if self.stack:
                value = self.stack.pop()
                self.stack.append(StackValue(f"not {value.expr}"))
            return None

        elif inst.mnemonic in ['and', 'or']:
            if len(self.stack) >= 2:
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(StackValue(f"({left.expr} {inst.mnemonic} {right.expr})"))
            return None

        # Control flow - handled separately
        elif inst.mnemonic in ['cmpeq', 'cmpne', 'cmplt', 'cmple', 'cmpgt', 'cmpge', 'jne', 'je', 'jmp']:
            return None

        elif inst.mnemonic == 'ret':
            return None

        elif inst.mnemonic == 'abrt':
            return "return"

        # Unknown
        else:
            ops = ', '.join(inst.operands) if inst.operands else ''
            return f"-- {inst.mnemonic} {ops}"

    def _translate_callis(self, inst: Instruction) -> Optional[str]:
        """Translate intrinsic function call."""
        if not inst.operands:
            return None

        # Parse function name and argument count
        parts = inst.operands[0].split('@')
        if len(parts) == 2:
            func_name = parts[0]
            arg_count = int(parts[1])
        else:
            # Try to parse as opcode
            try:
                if 'H' in inst.operands[0]:
                    opcode = int(inst.operands[0].replace('H', ''), 16)
                else:
                    opcode = int(inst.operands[0], 16)

                func_info = INTRINSIC_MAP.get(opcode)
                if func_info:
                    func_name = func_info[0]
                    arg_count = func_info[2]
                else:
                    func_name = f"unknown_{opcode:04X}H"
                    arg_count = int(inst.operands[1]) if len(inst.operands) > 1 else 0
            except:
                func_name = inst.operands[0]
                arg_count = int(inst.operands[1]) if len(inst.operands) > 1 else 0

        # Pop arguments from stack
        args = []
        for _ in range(arg_count):
            if self.stack:
                args.insert(0, self.stack.pop().expr)

        # Build call
        call_expr = f"{func_name}({', '.join(args)})"

        # Push result (some calls are used for their return values)
        self.stack.append(StackValue(call_expr))

        # Check if next instruction is pop - if so, this is a statement
        if self.pc + 1 < len(self.func.instructions):
            next_inst = self.func.instructions[self.pc + 1]
            if next_inst.mnemonic == 'pop':
                # Will be handled as assignment, don't output standalone
                return None

        # Standalone call
        return call_expr

    def _translate_calli(self, inst: Instruction) -> Optional[str]:
        """Translate internal function call."""
        if not inst.operands:
            return None

        # Parse like callis
        parts = inst.operands[0].split('@')
        if len(parts) == 2:
            func_name = parts[0]
            arg_count = int(parts[1])
        else:
            # Parse opcode
            opcode_str = inst.operands[0].replace('H', '')
            try:
                opcode = int(opcode_str, 16)
                func_name = f"func_{opcode:04X}"
            except:
                func_name = inst.operands[0]
            arg_count = int(inst.operands[1]) if len(inst.operands) > 1 else 0

        # Pop arguments
        args = []
        for _ in range(arg_count):
            if self.stack:
                args.insert(0, self.stack.pop().expr)

        call_expr = f"{func_name}({', '.join(args)})"
        self.stack.append(StackValue(call_expr))

        # Check if standalone
        if self.pc + 1 < len(self.func.instructions):
            next_inst = self.func.instructions[self.pc + 1]
            if next_inst.mnemonic == 'pop':
                return None

        return call_expr

    def _indent(self, text: str) -> str:
        """Add indentation."""
        return (self.indent_str * self.indent_level) + text

    def _convert_var_name(self, var_ref: str) -> str:
        """Convert variable reference like [0000] to var_0000."""
        if var_ref.startswith('[') and var_ref.endswith(']'):
            var_idx = var_ref[1:-1]
            return f"var_{var_idx}"
        return var_ref


def translate_function(func: UsecodeFunction) -> List[str]:
    """Translate a usecode function to Lua code lines."""
    translator = BytecodeTranslator(func)
    return translator.translate()
