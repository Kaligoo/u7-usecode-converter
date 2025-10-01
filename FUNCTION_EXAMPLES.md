# Function Examples - Converted Output

Examples of various types of functions converted from usecode to Lua.

---

## Example 1: Simple Empty Function (0x02E3)

**Type**: No-op / Placeholder

### Our Output
```lua
--[[
    Function: func_02E3
    Original Usecode: 0x02E3

    Args: 1
    Locals: 0
]]

function func_02E3(eventid, objectref)
    -- Original instructions:
    -- 0000: db   2c	???
    -- 0001: ret
end
```

**What it does**: Returns immediately, does nothing. Probably a placeholder or disabled function.

---

## Example 2: Simple Sound Effect (0x092C)

**Type**: Basic function call

### Our Output
```lua
--[[
    Function: func_092C
    Original Usecode: 0x092C

    Args: 1
    Locals: 0
]]

function func_092C(eventid, objectref)
    -- Original instructions:
    -- 0000: pushi      004BH                ; 75
    -- 0003: calli      000F, 1
    -- 0007: ret
end
```

**What it does**: Pushes value 75 (0x4B) and calls intrinsic function 0x000F. Likely plays a sound effect.

---

## Example 3: Close Gumps (0x00B2)

**Type**: Event-driven simple action

### Our Output
```lua
--[[
    Function: func_00B2
    Original Usecode: 0x00B2

    Args: 1
    Locals: 1
]]

-- Event types
local EVENT_BARK = 0
local EVENT_DOUBLECLICK = 1
local EVENT_USE = 2
local EVENT_EGG = 3
local EVENT_SPELL = 4
local EVENT_SPECIAL = 7

function func_00B2(eventid, objectref)
    local var_0000

    -- Original instructions:
    -- 0000: push       eventid
    -- 0001: pushi      0001H                ; 1
    -- 0004: cmpeq
    -- 0005: jne        000F
    -- 0008: callis 0048, 0 -> close_gumps() # Close all GUI windows
    -- 000C: pop        [0000]
    -- 000F: ret
end
```

**What it does**:
- Checks if `eventid == 1` (doubleclick)
- If yes, calls `close_gumps()` to close all GUI windows
- Returns

**Manual translation**:
```lua
function func_00B2(eventid, objectref)
    if eventid == EVENT_DOUBLECLICK then
        close_gumps()
    end
end
```

---

## Example 4: Ship Gangplank (0x0096)

**Type**: Multi-check validation

### Our Output
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
    -- Original instructions:
    -- 0000: push       eventid
    -- 0001: pushi      0001H                ; 1
    -- 0004: cmpeq
    -- 0005: jne        0038
    -- 0008: pushi      000AH                ; 10
    -- 000B: push       objectref
    -- 000C: callis 0088, 2 -> check_object_flag() # Check object flag state
    -- 0010: jne        001C
    -- 0013: pushs      L0000                ; @The sails must b...
    -- 0016: call       [0000]               ; 08FFH
    -- 0019: jmp        0038
    -- 001C: push       objectref
    -- 001D: call       [0001]               ; 0829H
    -- 0020: not
    -- 0021: jne        002D
    -- 0024: pushs      L0039                ; @I think the gang...
    -- 0027: call       [0000]               ; 08FFH
    -- 002A: jmp        0038
    -- 002D: callis 0081, 0 -> is_in_gump_mode() # Check if GUI is open
    -- 0031: jne        0038
    -- 0034: calli      007E, 0
    -- 0038: ret
end
```

**What it does**:
1. Check if event == doubleclick
2. Check if sails are furled (flag 10)
3. If not, show "sails must be furled" message
4. Check if gangplank path is clear
5. If not, show "gangplank blocked" message
6. Check if GUI is open, if so call function 0x007E

**Manual translation**:
```lua
local FLAG_SAILS_FURLED = 10

function ship_gangplank(eventid, objectref)
    if eventid ~= EVENT_DOUBLECLICK then
        return
    end

    if not check_object_flag(objectref, FLAG_SAILS_FURLED) then
        show_message(str_L0000)
        return
    end

    if not is_gangplank_clear(objectref) then
        show_message(str_L0039)
        return
    end

    if is_in_gump_mode() then
        close_gumps()
    end
end
```

---

## Example 5: Delegate Function (0x0501)

**Type**: Simple redirect

### Our Output
```lua
--[[
    Function: func_0501
    Original Usecode: 0x0501

    Args: 1
    Locals: 0
    External functions: 1
]]

function func_0501(eventid, objectref)
    -- Original instructions:
    -- 0000: push       objectref
    -- 0001: calle      0326H                ; 806
    -- 0004: ret
end
```

**What it does**: Calls external function 0x0326 (806) with objectref. This is a simple delegation pattern.

**Manual translation**:
```lua
function func_0501(eventid, objectref)
    func_0326(eventid, objectref)
end
```

---

## Example 6: Guard Dialogue (0x0326)

**Type**: Complex NPC conversation

### Our Output (truncated)
```lua
--[[
    Function: func_0326
    Original Usecode: 0x0326

    Args: 1
    Locals: 4
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
local str_L0000 = "bye"
local str_L0004 = "job"
local str_L0008 = "name"
local str_L000D = "password"
local str_L0016 = "You see a tough-looking guard who takes his job -very- seriously."
local str_L0058 = "name"
local str_L005D = "\"My name is not important.\""
local str_L0079 = "name"
local str_L007E = "job"
local str_L0082 = "\"I keep villains and knaves out of Trinsic and keep a record of all who leave. Thou must have a password to leave.\""
local str_L00F6 = "password"
local str_L00FF = "password"
local str_L0108 = "\"What is the password?\""
local str_L0120 = "Please"
local str_L0127 = "Long live the king"
local str_L013A = "Uhh, I don't know"
local str_L014C = "Blackbird"
local str_L0156 = "Blackbird"
local str_L0160 = "\"Very well, thou mayest pass.\"*"
local str_L0180 = "\"Thou dost not know the password. Sorry. The Mayor can give thee the proper password.\""
local str_L01D7 = "bye"
local str_L01DB = "\"Goodbye.\"*"

function func_0326(eventid, objectref)
    local var_0000, var_0001, var_0002, var_0003

    -- Original instructions:
    -- 0000: push       eventid
    -- 0001: pushi      0000H                ; 0
    -- 0004: cmpeq
    -- 0005: jne        0009
    -- 0008: abrt
    -- 0009: push       objectref
    -- 000A: callis 001B, 1 -> get_npc_object() # Get NPC object reference
    -- 000E: callis 001C, 1 -> get_schedule() # Get NPC schedule type
    -- 0012: pop        [0000]
    -- 0015: pushi      0000H                ; 0
    -- ... and 70 more instructions
end
```

**What it does**:
- NPC guard at Trinsic gate
- Checks player's schedule
- Handles conversation about password
- Keyword responses: "name", "job", "password", "bye"
- Password check: "Blackbird" is correct
- Multiple dialogue branches

**Benefits of our output**:
- All dialogue strings extracted and labeled
- Intrinsic functions identified (get_npc_object, get_schedule)
- Clear instruction-by-instruction breakdown
- Event types documented

---

## Comparison: Old vs New

### Old Conversion (from U7Revisited)
```lua
function func_0096(eventid, objectref)
    if eventid == 1 then
        if not unknown_0088H(10, objectref) then
            unknown_08FFH("@The sails must be furled...")
        elseif not unknown_0829H(objectref) then
            unknown_08FFH("@I think the gangplank...")
        elseif not unknown_0081H() then
            unknown_007EH()
        end
    end
end
```

**Problems**:
- ❌ No documentation
- ❌ Mystery functions (`unknown_0088H`, etc.)
- ❌ Magic numbers
- ❌ Strings inline (can't reuse)

### New Conversion
```lua
--[[
    Function: func_0096
    Args: 1, Locals: 0
]]

-- Event types
local EVENT_DOUBLECLICK = 1

-- String data
local str_L0000 = "@The sails must be furled..."
local str_L0039 = "@I think the gangplank..."

function func_0096(eventid, objectref)
    -- 000C: callis 0088, 2 -> check_object_flag() # Check object flag state
    -- 0016: call [0000] ; 08FFH
    -- 0027: call [0000] ; 08FFH
    -- 002D: callis 0081, 0 -> is_in_gump_mode() # Check if GUI is open
end
```

**Improvements**:
- ✅ Header documentation
- ✅ Functions identified: `check_object_flag()`, `is_in_gump_mode()`
- ✅ Event constants
- ✅ Extracted strings
- ✅ Clear instruction comments

---

## Summary

The converter generates Lua with:

1. **Header comments** - Function metadata
2. **Event constants** - Named event types
3. **String extraction** - Dialogue as local variables
4. **Intrinsic mapping** - Shows what unknown functions do
5. **Instruction breakdown** - Every bytecode instruction documented

This makes **manual translation much easier** and provides a **solid foundation for automated translation** in the next phase!
