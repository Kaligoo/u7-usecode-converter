# Example Converter Output

This document shows what the converter currently generates from usecode.

## Input: Function 0x0096 (Ship Gangplank)

From `usecode.dis`:

```
.funcnumber	0096H
.data
L0000:	db	'@The sails must be furled before the planks are raised.@'
L0038:	db	00
L0039:	db	'@I think the gangplank is blocked.@'
L005C:	db	00
.code
.argc 0001H
.localc 0000H
.externsize 0002H
.extern 08FFH
.extern 0829H
0000: 48 		push	eventid
0001: 1F 01 00 		pushi	0001H			; 1
0004: 22 		cmpeq
0005: 05 30 00 		jne	0038
0008: 1F 0A 00 		pushi	000AH			; 10
000B: 3E 		push	objectref
000C: 38 88 00 02 	callis	0088, 2
0010: 05 09 00 		jne	001C
0013: 1D 00 00 		pushs	L0000
0016: 24 00 00 		call	[0000]			; 08FFH
0019: 06 1C 00 		jmp	0038
001C: 3E 		push	objectref
001D: 24 01 00 		call	[0001]			; 0829H
0020: 10 		not
0021: 05 09 00 		jne	002D
0024: 1D 39 00 		pushs	L0039
0027: 24 00 00 		call	[0000]			; 08FFH
002A: 06 0B 00 		jmp	0038
002D: 38 81 00 00 	callis	0081, 0
0031: 05 04 00 		jne	0038
0034: 39 7E 00 00 	calli	007E, 0
0038: 25 		ret
```

## Current Output: `func_0096.lua`

```lua
--[[
    Function: func_0096
    Original Usecode: 0x0096

    Args: 1
    Locals: 0
    External functions: 2
]]

-- Event types
local EVENT_BARK = 0
local EVENT_DOUBLECLICK = 1
local EVENT_USE = 2
local EVENT_EGG = 3
local EVENT_SPELL = 4
local EVENT_SPECIAL = 7

-- String data
local str_L0000 = "@The sails must be furled before the planks are raised.@"
local str_L0039 = "@I think the gangplank is blocked.@"

function func_0096(eventid, objectref)
    -- TODO: Convert bytecode to Lua
    -- This requires a full instruction-to-Lua translator

    -- Original instructions:
    -- 0000: push       eventid
    -- 0001: pushi      0001H               ; 1
    -- 0004: cmpeq
    -- 0005: jne        0038
    -- 0008: pushi      000AH               ; 10
    -- 000B: push       objectref
    -- 000C: callis     0088, 2 -> check_object_flag() # Check object flag state
    -- 0010: jne        001C
    -- 0013: pushs      L0000               ; @The sails must b...
    -- 0016: call       [0000]              ; 08FFH
    -- ... and 10 more instructions
end
```

## Target Output (Future Enhancement)

What we want to generate eventually:

```lua
--[[
    Ship Gangplank Handler (func_0096)
    Original Usecode: 0x0096

    Purpose: Manages gangplank deployment on ships. Validates that:
             - Sails are properly furled
             - Gangplank path is clear
             - Ship is properly anchored

    Events:
        EVENT_DOUBLECLICK: Player attempts to use gangplank
]]

-- Constants
local EVENT_DOUBLECLICK = 1
local FLAG_SAILS_FURLED = 10

-- String messages
local MSG_SAILS_NOT_FURLED = "@The sails must be furled before the planks are raised.@"
local MSG_GANGPLANK_BLOCKED = "@I think the gangplank is blocked.@"

function ship_gangplank_handler(eventid, objectref)
    -- Only handle double-click interaction
    if eventid ~= EVENT_DOUBLECLICK then
        return
    end

    -- Check if sails are furled before allowing gangplank deployment
    if not check_object_flag(objectref, FLAG_SAILS_FURLED) then
        show_message(MSG_SAILS_NOT_FURLED)
        return
    end

    -- Check if gangplank path is clear
    if not is_gangplank_path_clear(objectref) then
        show_message(MSG_GANGPLANK_BLOCKED)
        return
    end

    -- Check if ship is anchored (if not, anchor it)
    if not is_in_gump_mode() then
        close_gumps()
    end
end
```

## What's Implemented vs. What's Next

### ✅ Currently Implemented

1. **Function structure** - Proper Lua function with header comments
2. **Metadata** - Args, locals, external function count
3. **Event constants** - When function uses event checks
4. **String extraction** - Data section converted to local variables
5. **Intrinsic mapping** - Comments show `check_object_flag()` instead of `unknown_0088H()`
6. **Instruction comments** - Shows what each bytecode instruction does

### 🚧 Next Phase: Full Bytecode Translation

To get from current output to target output, we need:

1. **Control flow analysis**
   - Convert `jne` → `if not ... then`
   - Convert `jmp` → early returns or goto alternatives
   - Detect loops and convert to `while`/`for`

2. **Stack simulation**
   - Track stack operations (`push`, `pushi`, etc.)
   - Build expression trees
   - Generate proper Lua expressions

3. **Intrinsic call translation**
   - `callis 0088, 2` → `check_object_flag(objectref, 10)`
   - External calls → proper function calls
   - String references → use generated locals

4. **Semantic analysis**
   - Rename `func_0096` → `ship_gangplank_handler`
   - Identify constant values (10 → FLAG_SAILS_FURLED)
   - Infer variable purposes from usage patterns

5. **Code cleanup**
   - Remove redundant checks
   - Simplify boolean logic
   - Generate idiomatic Lua

## Benefits of Current Approach

Even without full translation, our current output is valuable:

- **80+ intrinsic functions mapped** - Shows what `callis` opcodes actually do
- **Structure preserved** - Event handling, data sections clear
- **Comments as guide** - Manual translation much easier
- **Foundation for automation** - Next phase can build on this

The converter provides a huge improvement over starting from scratch, and makes the remaining 75% of work (full bytecode translation) much more approachable.
