# U7 Usecode to Lua Converter

An improved converter for translating Ultima 7's usecode scripts to Lua for the [U7Revisited](https://github.com/ViridianGames/U7Revisited) project.

## Overview

The U7Revisited project is reimplementing Ultima VII: The Black Gate with a new engine. The original game used a proprietary bytecode scripting system called "usecode". This converter translates usecode to modern, readable Lua scripts.

### Current Problem

Existing conversions (approx. 25% working) suffer from:
- ❌ Incomplete intrinsic function mapping (many `unknown_XXXXH()` placeholders)
- ❌ Generic variable names (`var_0000`, `var_0001`, etc.)
- ❌ No comments or documentation
- ❌ Magic numbers everywhere
- ❌ Lost semantic meaning from mechanical translation

### Our Goal

Create **better quality** Lua conversions that are:
- ✅ Functionally complete (all intrinsics mapped)
- ✅ Readable (semantic variable names where possible)
- ✅ Documented (comments explaining game mechanics)
- ✅ Maintainable (named constants, clear structure)
- ✅ Idiomatic Lua (not just bytecode translation)

## Project Status

🚧 **In Development**

### Completed
- [x] Repository setup
- [x] Analyzed U7Revisited engine Lua API
- [x] Mapped intrinsic functions (partial)
- [x] Studied usecode.dis format

### In Progress
- [ ] Complete intrinsic function mapping
- [ ] Build usecode parser
- [ ] Implement Lua code generator
- [ ] Test conversions

## Files

- **`intrinsic_mapping.py`** - Mapping of usecode intrinsics to Lua API functions
- **`usecode_parser.py`** - Parser for usecode.dis format _(coming soon)_
- **`lua_generator.py`** - Generates improved Lua code _(coming soon)_
- **`converter.py`** - Main conversion tool _(coming soon)_

## How It Works

### Input: `usecode.dis`
```
.funcnumber	0096H
.data
L0000:	db	'@The sails must be furled before the planks are raised.@'
.code
.argc 0001H
push	eventid
pushi	01H
cmpeq
jne	L000D
callis	0088H, 2
```

### Output: Improved Lua
```lua
--[[
    Ship Gangplank Handler (func_0096)
    Original Usecode: 0x0096
    Purpose: Manages gangplank deployment on ships
]]

local EVENT_DOUBLECLICK = 1
local FLAG_SAILS_FURLED = 10

function ship_gangplank_handler(eventid, objectref)
    if eventid ~= EVENT_DOUBLECLICK then
        return
    end

    if not check_object_flag(objectref, FLAG_SAILS_FURLED) then
        show_message("@The sails must be furled before the planks are raised.@")
        return
    end
    -- ...
end
```

## Resources

### U7Revisited Engine
- **Lua API**: `Source/U7LuaFuncs.cpp`
- **Existing Scripts**: `Redist/Data/Scripts/`
- **Documentation**: `SCRIPTING_GUIDE.md`

### Usecode Documentation
- **Disassembly**: `Redist/Data/usecode.dis` - Original bytecode
- **Decompiled**: `usecode.dc` - C-like decompilation
- **Exult Project**: https://github.com/exult/exult (reference implementation)

## Event Types

| Event | Name | Description |
|-------|------|-------------|
| 0 | bark | Text appears over character's head |
| 1 | doubleclick | Player double-clicks object |
| 2 | use | Use action (object on object, or NPC dialogue) |
| 3 | egg | Triggered by proximity/conditions |
| 4 | spell | Spell-related events |
| 7 | special | Special game events |

## Contributing

This is a focused tool for the U7Revisited conversion effort. Improvements welcome!

1. Study existing Lua scripts in U7Revisited
2. Test conversions against the actual engine
3. Document new intrinsic mappings discovered
4. Improve semantic analysis for better variable naming

## License

This is a community tool for the U7Revisited project. See the main project for game-related licensing.

---

**Note**: Ultima VII is © Origin Systems / Electronic Arts. This tool is for converting game scripts to work with the open-source U7Revisited engine.
