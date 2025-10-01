"""
Lua Code Generator for Usecode

Converts parsed usecode functions into readable Lua scripts.
"""

from typing import List, Dict, Optional, Set
from usecode_parser import UsecodeFunction, Instruction, DataSegment
from intrinsic_mapping import get_lua_function, get_function_description, EVENT_TYPES


class LuaGenerator:
    """Generates Lua code from parsed usecode."""

    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces

    def generate_function(self, func: UsecodeFunction, func_name: Optional[str] = None) -> str:
        """Generate complete Lua function from usecode."""
        lines = []

        # Generate header comment
        lines.extend(self._generate_header(func, func_name))
        lines.append("")

        # Generate constants for event types if needed
        if self._uses_event_checks(func):
            lines.extend(self._generate_event_constants())
            lines.append("")

        # Generate data segment as local strings
        if func.data_segments:
            lines.extend(self._generate_data_section(func))
            lines.append("")

        # Generate function signature
        func_name = func_name or f"func_{func.func_number:04X}"
        params = self._generate_parameters(func)
        lines.append(f"function {func_name}({params})")

        # Generate local variables
        if func.localc > 0:
            lines.extend(self._generate_locals(func))
            lines.append("")

        # Generate function body (convert instructions to Lua)
        self.indent_level = 1
        body = self._generate_body(func)
        lines.extend(body)

        # Close function
        lines.append("end")
        lines.append("")

        return "\n".join(lines)

    def _generate_header(self, func: UsecodeFunction, func_name: Optional[str]) -> List[str]:
        """Generate function header comment."""
        name = func_name or f"func_{func.func_number:04X}"
        lines = [
            "--[[",
            f"    Function: {name}",
            f"    Original Usecode: 0x{func.func_number:04X}",
            f"    ",
            f"    Args: {func.argc}",
            f"    Locals: {func.localc}",
        ]

        if func.external_funcs:
            lines.append(f"    External functions: {len(func.external_funcs)}")

        lines.append("]]")
        return lines

    def _generate_event_constants(self) -> List[str]:
        """Generate event type constants."""
        lines = ["-- Event types"]
        for event_id, event_name in sorted(EVENT_TYPES.items()):
            const_name = f"EVENT_{event_name.upper()}"
            lines.append(f"local {const_name} = {event_id}")
        return lines

    def _generate_data_section(self, func: UsecodeFunction) -> List[str]:
        """Generate local string variables from data section."""
        lines = ["-- String data"]

        for segment in func.data_segments:
            if segment.is_string and segment.data:
                # Create a variable name from the label
                var_name = f"str_{segment.label}"
                # Escape quotes in string
                escaped_data = str(segment.data).replace('"', '\\"')
                lines.append(f'local {var_name} = "{escaped_data}"')

        return lines

    def _generate_parameters(self, func: UsecodeFunction) -> str:
        """Generate function parameters."""
        # Standard usecode parameters
        params = ["eventid", "objectref"]

        # Add additional args if needed
        if func.argc > 2:
            for i in range(2, func.argc):
                params.append(f"arg{i}")

        return ", ".join(params)

    def _generate_locals(self, func: UsecodeFunction) -> List[str]:
        """Generate local variable declarations."""
        if func.localc == 0:
            return []

        # Generate var_0000, var_0001, etc.
        vars = [f"var_{i:04X}" for i in range(func.localc)]
        return [self._indent(f"local {', '.join(vars)}")]

    def _generate_body(self, func: UsecodeFunction) -> List[str]:
        """Generate function body from instructions."""
        lines = []

        # For now, generate a simple comment-based representation
        # Full implementation would convert each instruction to Lua
        lines.append(self._indent("-- TODO: Convert bytecode to Lua"))
        lines.append(self._indent("-- This requires a full instruction-to-Lua translator"))
        lines.append("")

        # Show basic structure
        lines.append(self._indent("-- Original instructions:"))
        for inst in func.instructions[:10]:  # Show first 10
            comment = self._format_instruction_comment(inst, func)
            lines.append(self._indent(f"-- {inst.address:04X}: {comment}"))

        if len(func.instructions) > 10:
            lines.append(self._indent(f"-- ... and {len(func.instructions) - 10} more instructions"))

        return lines

    def _format_instruction_comment(self, inst: Instruction, func: UsecodeFunction) -> str:
        """Format instruction as a comment."""
        ops = ", ".join(inst.operands) if inst.operands else ""

        # Special formatting for intrinsic calls
        if inst.mnemonic == "callis" and inst.operands:
            # Extract opcode
            opcode_str = inst.operands[0].replace('H', '')
            try:
                opcode = int(opcode_str, 16)
                lua_func = get_lua_function(opcode)
                desc = get_function_description(opcode)
                return f"{inst.mnemonic} {ops} -> {lua_func}() # {desc}"
            except (ValueError, IndexError):
                pass

        # Format with comment if available
        if inst.comment:
            return f"{inst.mnemonic:10s} {ops:20s} ; {inst.comment}"

        return f"{inst.mnemonic:10s} {ops}"

    def _uses_event_checks(self, func: UsecodeFunction) -> bool:
        """Check if function uses event type comparisons."""
        # Look for "push eventid" followed by pushi and cmpeq
        for i, inst in enumerate(func.instructions):
            if inst.mnemonic == "push" and "eventid" in inst.operands:
                # Check next few instructions for comparison
                if i + 2 < len(func.instructions):
                    next_inst = func.instructions[i + 1]
                    if next_inst.mnemonic == "pushi":
                        return True
        return False

    def _indent(self, text: str) -> str:
        """Add indentation to text."""
        return (self.indent_str * self.indent_level) + text


def generate_lua_script(func: UsecodeFunction, func_name: Optional[str] = None) -> str:
    """Convenience function to generate Lua from a usecode function."""
    generator = LuaGenerator()
    return generator.generate_function(func, func_name)


if __name__ == '__main__':
    # Test generator
    import sys
    from usecode_parser import parse_usecode_file

    if len(sys.argv) < 2:
        print("Usage: python lua_generator.py <usecode.dis> [function_number_hex]")
        sys.exit(1)

    functions = parse_usecode_file(sys.argv[1])

    if len(sys.argv) >= 3:
        # Generate specific function
        func_num = int(sys.argv[2], 16)
        if func_num in functions:
            lua_code = generate_lua_script(functions[func_num])
            print(lua_code)
        else:
            print(f"Function 0x{func_num:04X} not found")
    else:
        # Generate first function as example
        first_func = list(functions.values())[0]
        lua_code = generate_lua_script(first_func)
        print(lua_code)
        print(f"\n-- Total functions available: {len(functions)}")
