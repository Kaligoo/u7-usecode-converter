"""
U7 Usecode to Lua Converter

Main converter script that coordinates parsing and code generation.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List

from usecode_parser import parse_usecode_file, UsecodeFunction
from lua_generator import generate_lua_script


def convert_usecode_file(
    input_file: str,
    output_dir: str,
    func_numbers: Optional[List[int]] = None,
    verbose: bool = False
) -> int:
    """
    Convert usecode.dis to Lua scripts.

    Args:
        input_file: Path to usecode.dis
        output_dir: Output directory for Lua files
        func_numbers: List of specific function numbers to convert (None = all)
        verbose: Print progress information

    Returns:
        Number of functions converted
    """
    # Parse usecode file
    if verbose:
        print(f"Parsing {input_file}...")

    try:
        functions = parse_usecode_file(input_file)
    except Exception as e:
        print(f"Error parsing usecode file: {e}", file=sys.stderr)
        return 0

    if verbose:
        print(f"Found {len(functions)} functions")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Determine which functions to convert
    if func_numbers:
        to_convert = {num: functions[num] for num in func_numbers if num in functions}
        if len(to_convert) < len(func_numbers):
            missing = set(func_numbers) - set(functions.keys())
            print(f"Warning: Functions not found: {[f'0x{n:04X}' for n in missing]}")
    else:
        to_convert = functions

    # Convert each function
    converted = 0
    for func_num, func in to_convert.items():
        try:
            # Generate Lua code
            lua_code = generate_lua_script(func)

            # Write to file
            output_file = os.path.join(output_dir, f"func_{func_num:04X}.lua")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(lua_code)

            converted += 1

            if verbose:
                print(f"  Converted 0x{func_num:04X} -> {output_file}")

        except Exception as e:
            print(f"Error converting function 0x{func_num:04X}: {e}", file=sys.stderr)

    return converted


def main():
    parser = argparse.ArgumentParser(
        description="Convert Ultima 7 usecode to Lua scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all functions
  python converter.py usecode.dis output/

  # Convert specific functions
  python converter.py usecode.dis output/ --functions 0096 009A

  # Verbose output
  python converter.py usecode.dis output/ -v
        """
    )

    parser.add_argument(
        'input',
        help='Path to usecode.dis file'
    )

    parser.add_argument(
        'output',
        help='Output directory for Lua files'
    )

    parser.add_argument(
        '--functions', '-f',
        nargs='+',
        metavar='HEX',
        help='Specific function numbers to convert (hex, e.g., 0096 009A)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print verbose progress information'
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Parse function numbers if provided
    func_numbers = None
    if args.functions:
        try:
            func_numbers = [int(f, 16) for f in args.functions]
        except ValueError as e:
            print(f"Error: Invalid function number: {e}", file=sys.stderr)
            sys.exit(1)

    # Run converter
    converted = convert_usecode_file(
        args.input,
        args.output,
        func_numbers,
        args.verbose
    )

    # Print summary
    if args.verbose or converted > 0:
        print(f"\nConverted {converted} function(s) to {args.output}/")

    sys.exit(0 if converted > 0 else 1)


if __name__ == '__main__':
    main()
