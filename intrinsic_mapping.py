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
    # === Conversation System ===
    0x0003: ('second_speaker', 'Set secondary speaker in conversation', 3),  # (npc_id, frame, dialog)
    0x0004: ('hide_npc', 'Hide NPC portrait in conversation', 1),  # (npc_id)
    0x0005: ('add_answer', 'Add dialogue answer options', 1),  # (answers)
    0x0006: ('remove_answer', 'Remove dialogue answer options', 1),  # (answers)
    0x0007: ('save_answers', 'Save current answer state', 0),
    0x0008: ('restore_answers', 'Restore saved answer state', 0),
    0x000A: ('get_answer', 'Get player\'s dialogue choice', 0),
    0x000B: ('ask_yes_no', 'Present Yes/No choice', 0),
    0x000C: ('ask_number', 'Ask player for numeric input', 4),  # (min, max, step, default)
    0x0033: ('object_select_modal', 'Show object selection dialog', 0),  # Was start_conversation in some contexts

    # === Object Manipulation ===
    0x000D: ('set_object_shape', 'Set object shape ID', 2),  # (object_id, shape)
    0x0011: ('get_object_shape', 'Get object shape ID', 1),  # (object_id)
    0x0012: ('get_object_frame', 'Get object frame number', 1),  # (object_id)
    0x0013: ('set_object_frame', 'Set object frame number', 2),  # (object_id, frame)
    0x0014: ('get_object_quality', 'Get object quality value', 1),  # (object_id)
    0x0015: ('set_object_quality', 'Set object quality value', 2),  # (object_id, quality)
    0x0024: ('spawn_object', 'Create new object', 1),  # (shape) - returns object ref
    0x0025: ('set_last_created', 'Mark object as last_created', 1),  # (object_id)
    0x0026: ('set_object_position', 'Set object position', 1),  # (object_id) - uses position from stack

    # === NPC & Character ===
    0x001B: ('get_npc_object', 'Get NPC object reference', 1),  # (npc_id)
    0x001C: ('get_schedule', 'Get NPC schedule type', 1),  # (npc_id)
    0x0020: ('get_npc_property', 'Get NPC property value', 2),  # (npc_id, property_id)
    0x0021: ('set_npc_property', 'Set NPC property value', 3),  # (npc_id, property_id, value)
    0x0022: ('get_active_player', 'Get avatar/player reference', 0),  # Returns avatar object
    0x0027: ('get_player_name', 'Get player/NPC name', 1),  # (npc_id)
    0x0031: ('is_npc', 'Check if object is an NPC', 1),  # (object_id)

    # === Party Management ===
    0x0023: ('get_party_members', 'Get list of party member names', 0),
    0x002F: ('npc_id_in_party', 'Check if NPC ID is in party', 1),  # (npc_id)
    0x0030: ('add_to_party', 'Add NPC to party', 1),  # (npc_id)

    # === Container/Inventory ===
    0x0001: ('add_to_container', 'Add item to container', 2),  # (container_id, item_id)
    0x0002: ('remove_from_container', 'Remove item from container', 3),  # (item_id, count, something)
    0x002A: ('get_container_objects', 'Get objects in container', 4),  # (container_id, shape, quality, frame)
    0x006E: ('get_container', 'Get container holding object', 1),  # (object_id)

    # === Position & Movement ===
    0x0018: ('get_object_position', 'Get object position', 1),  # (object_id) - returns [x, y, z]
    0x0019: ('get_distance', 'Get distance between objects', 2),  # (obj1, obj2)
    0x001A: ('get_direction', 'Get direction from object to target', 2),  # (from, to)
    0x0035: ('check_in_range', 'Check if object in range', 4),  # (object, x, y, range)
    0x0085: ('is_not_blocked', 'Check if position not blocked', 3),  # (x, y, z?)

    # === World/Time ===
    0x0038: ('get_time_hour', 'Get current game hour', 0),
    0x0039: ('get_time_minute', 'Get current game minute', 0),

    # === Audio/Visual ===
    0x002E: ('play_music', 'Play music track', 2),  # (object_id, song_num)
    0x0040: ('bark', 'Display text near object', 2),  # (object_id, text)
    0x0051: ('play_sound_effect', 'Play sound effect', 1),  # (sound_id)
    0x0054: ('sprite_effect', 'Play visual effect', 3),  # (effect_id, x, y)

    # === Game State ===
    0x0048: ('close_gumps', 'Close all GUI windows', 0),
    0x0058: ('is_in_usecode', 'Check if in usecode execution', 1),  # (object_id)
    0x0062: ('get_avatar_ref', 'Get avatar object reference', 0),
    0x0068: ('detect_mouse', 'Check if mouse exists', 0),
    0x0079: ('in_usecode', 'Mark object as in usecode', 1),  # (object_id)
    0x0081: ('is_in_gump_mode', 'Check if GUI is open', 0),
    0x0088: ('check_object_flag', 'Check object flag state', 2),  # (object, flag)

    # === Utility ===
    0x0000: ('random', 'Get random number', 1),  # (max) - Exult intrinsic 0x00 is UI_get_random
    0x0010: ('random2', 'Get random number in range', 2),  # (min, max)
    0x005E: ('array_size', 'Get array size', 1),  # (array)
    0x0072: ('execute_usecode_array', 'Execute embedded usecode', 4),  # Complex bytecode execution
    0x007D: ('add_containerobject_s', 'Add multiple items to container', 2),  # (container, items_array)
    0x003A: ('some_check', 'Unknown check function', 1),  # Needs investigation
    0x003B: ('another_check', 'Unknown check function', 0),  # Needs investigation

    # === Combat/Effects ===
    0x0090: ('hit_object', 'Apply damage or hit effect', 1),  # (object_id)

    # === Searching ===
    0x000E: ('find_nearest', 'Find nearest object of type', 3),  # (from_obj, shape, range)
    0x0028: ('count_objects', 'Count objects matching criteria', 4),  # (container?, shape, quality, frame?)
    0x002B: ('add_party_items', 'Add items to party inventory', 5),  # Complex
    0x002C: ('remove_party_items', 'Remove items from party', 5),  # Complex

    # === Navigation/Pathfinding ===
    0x0036: ('set_path_failure', 'Set path failure handler', 1),  # (usecode_func)

    # === Miscellaneous ===
    0x0016: ('set_item_quantity', 'Set item quantity', 2),  # (object_id, quantity)
    0x0017: ('create_new_object', 'Advanced object creation', 2),  # (shape, frame?)
    0x0029: ('click_on_item', 'Simulate click on item', 1),  # (object_id)
    0x0037: ('update_last_created', 'Update last created object', 1),  # (object_id)
    0x0041: ('sprite_effect_at_position', 'Play sprite effect at position', 3),  # (effect, x, y)
    0x0042: ('set_timer', 'Set timer', 2),  # (duration, callback?)
    0x0044: ('get_timer', 'Get timer value', 1),  # (timer_id?)
    0x0047: ('cause_light', 'Create light effect', 1),  # (intensity?)
    0x004A: ('set_attack_mode', 'Set NPC attack mode', 1),  # (mode)
    0x004D: ('get_barge', 'Get barge object', 1),  # (object_id)
    0x0052: ('sit_down', 'Make NPC sit', 1),  # (npc_id)
    0x0065: ('die_roll', 'Roll dice', 2),  # (count, sides?)
    0x0067: ('earthquake', 'Trigger earthquake effect', 1),  # (intensity?)
    0x0069: ('is_water', 'Check if position is water', 1),  # (position?)
    0x006B: ('get_lift', 'Get object lift/z-level', 1),  # (object_id)
    0x006D: ('set_lift', 'Set object lift/z-level', 2),  # (object_id, lift)
    0x0074: ('lightning', 'Trigger lightning effect', 1),  # (target?)
    0x0087: ('flash_mouse', 'Flash mouse cursor', 0),
    0x008D: ('fade_palette', 'Fade screen palette', 1),  # (duration?)
    0x008E: ('armageddon', 'Trigger armageddon', 0),
    0x008F: ('resurrection', 'Resurrect NPC', 1),  # (npc_id?)
    0x0093: ('obj_sprite_effect', 'Play sprite effect on object', 2),  # (object_id, effect_id)
    0x0096: ('set_orrery', 'Set orrery state', 1),  # (state?)
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
