"""
Usecode Intrinsic Function to Lua API Mapping

This file contains the mapping between Ultima 7's usecode intrinsic functions
(identified by opcode numbers) and the U7Revisited Lua API functions.

Based on analysis of:
- U7Revisited/Source/U7LuaFuncs.cpp
- U7Revisited/Redist/Data/usecode.dc
- Exult usecode documentation

Format: opcode -> (lua_function_name, description, parameter_count)
"""

INTRINSIC_MAP = {
    # Conversation System
    0x0003: ('second_speaker', 'Set secondary speaker in conversation', 3),  # (npc_id, frame, dialog)
    0x0004: ('hide_npc', 'Hide NPC portrait in conversation', 1),  # (npc_id)
    0x0005: ('add_answer', 'Add dialogue answer options', 1),  # (answers)
    0x0006: ('remove_answer', 'Remove dialogue answer options', 1),  # (answers)
    0x0007: ('save_answers', 'Save current answer state', 0),
    0x0008: ('restore_answers', 'Restore saved answer state', 0),
    0x000A: ('get_answer', 'Get player\'s dialogue choice', 0),
    0x000B: ('ask_yes_no', 'Present Yes/No choice', 0),
    0x000C: ('ask_number', 'Ask player for numeric input', 4),  # (min, max, step, default)
    0x0033: ('start_conversation', 'Initialize conversation system', 0),

    # Object Manipulation
    0x000D: ('set_object_shape', 'Set object shape ID', 2),  # (object_id, shape)
    0x0011: ('get_object_shape', 'Get object shape ID', 1),  # (object_id)
    0x0012: ('get_object_frame', 'Get object frame number', 1),  # (object_id)
    0x0013: ('set_object_frame', 'Set object frame number', 2),  # (object_id, frame)
    0x0014: ('get_object_quality', 'Get object quality value', 1),  # (object_id)

    # NPC Properties
    0x0020: ('get_npc_property', 'Get NPC property value', 2),  # (npc_id, property_id)
    0x0021: ('set_npc_property', 'Set NPC property value', 3),  # (npc_id, property_id, value)
    0x0027: ('get_player_name', 'Get player/NPC name', 1),  # (npc_id)

    # Party Management
    0x0023: ('get_party_members', 'Get list of party member names', 0),
    0x002F: ('npc_id_in_party', 'Check if NPC ID is in party', 1),  # (npc_id)

    # Container/Inventory
    0x002A: ('get_container_objects', 'Get objects in container', 3),  # (container_id, type, quality)

    # World/Time
    0x0038: ('get_time_hour', 'Get current game hour', 0),
    0x0039: ('get_time_minute', 'Get current game minute', 0),

    # Audio/Visual
    0x002E: ('play_music', 'Play music track', 2),  # (object_id, song_num)
    0x0040: ('bark', 'Display text near object', 2),  # (object_id, text)

    # Player Info
    0x005A: ('is_player_female', 'Check if player is female', 0),

    # Utility
    # Note: random() is a custom Lua function, not from intrinsics
}

# UI_* functions from usecode.dc decompilation
# These need to be mapped to Lua equivalents
UI_FUNCTION_MAP = {
    'UI_get_item_flag': ('check_object_flag', 'Check object flag state', 2),  # (object, flag)
    'UI_in_gump_mode': ('is_conversation_running', 'Check if GUI is open', 0),
    'UI_close_gumps': ('close_gumps', 'Close all GUI windows', 0),
    'UI_find_nearest': ('find_nearest', 'Find nearest object of type', 3),  # (from_obj, shape, range)
    'UI_get_random': ('random', 'Get random number', 2),  # (min, max) - Lua uses random(lo, hi)
    'UI_item_say': ('bark', 'Make object display text', 2),  # (object, text)
    'UI_get_object_position': ('get_object_position', 'Get object coordinates', 1),  # (object)
    'UI_remove_item': ('destroy_object', 'Remove object from world', 1),  # (object)
    'UI_sprite_effect': ('sprite_effect', 'Play visual effect', 7),  # (effect, x, y, z, ...)
    'UI_play_sound_effect': ('play_sound_effect', 'Play sound', 1),  # (sound_id)
    'UI_get_schedule': ('get_schedule', 'Get NPC schedule', 1),  # (npc_id)
    'UI_set_schedule': ('set_schedule', 'Set NPC schedule', 2),  # (npc_id, schedule)
}

# Known unknown functions from existing Lua scripts
# These appear in converted scripts but aren't implemented
UNKNOWN_FUNCTIONS = {
    0x0018: 'get_object_position',  # Returns [x, y, z]
    0x0035: 'check_range_or_position',  # Complex position queries
    0x0044: 'unknown_condition_check',
    0x006F: 'unknown_object_manipulation',
    0x007E: 'close_gumps_or_anchors',  # Likely UI_close_gumps
    0x0081: 'is_in_gump_mode',  # Likely UI_in_gump_mode
    0x0088: 'check_object_flag',  # UI_get_item_flag
    0x008B: 'unknown_operation',
    0x008F: 'unknown_check',
    0x08FF: 'show_message',  # Display system message (bark)
    0x0829: 'check_gangplank_position',  # Game-specific function
    0x0900: 'unknown_getter',
    0x0903: 'unknown_setter',
    0x090C: 'display_options_wrapper',
    0x091B: 'format_price_string',
    0x0910: 'get_npc_property_alt',
    0x0912: 'set_npc_property_alt',
}

# Event types
EVENT_TYPES = {
    0: 'bark',
    1: 'doubleclick',
    2: 'use',
    3: 'egg',
    4: 'spell',
    7: 'special',
}

# Common object flags (partially documented)
OBJECT_FLAGS = {
    0x0A: 'SAILS_FURLED',
    # More flags need to be documented
}

def get_lua_function(opcode):
    """Get Lua function name for a usecode intrinsic opcode."""
    if opcode in INTRINSIC_MAP:
        return INTRINSIC_MAP[opcode][0]
    return f'unknown_{opcode:04X}H'

def get_function_description(opcode):
    """Get description for a usecode intrinsic opcode."""
    if opcode in INTRINSIC_MAP:
        return INTRINSIC_MAP[opcode][1]
    if opcode in UNKNOWN_FUNCTIONS:
        return UNKNOWN_FUNCTIONS[opcode]
    return 'Unknown function'

def get_param_count(opcode):
    """Get expected parameter count for a usecode intrinsic opcode."""
    if opcode in INTRINSIC_MAP:
        return INTRINSIC_MAP[opcode][2]
    return None  # Unknown

def translate_ui_function(ui_func_name):
    """Translate UI_* function name to Lua equivalent."""
    if ui_func_name in UI_FUNCTION_MAP:
        return UI_FUNCTION_MAP[ui_func_name][0]
    # Strip UI_ prefix and convert to snake_case as fallback
    return ui_func_name.replace('UI_', '').lower()
