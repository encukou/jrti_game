# This file regenerates itself

from pyglet.window import key


if __name__ == '__main__':
    with open(__file__) as f:
        for line in f:
            print(line, end='')
            if line.strip() == '####':
                break

    NAMES = {
        # Based in part on:
        # https://wincent.com/wiki/Unicode_representations_of_modifier_keys
        'SPACE': '␣',
        'ENTER': '⏎',
        'RETURN': '⏎',
        'BACKSPACE': '⌫',
        'DELETE': '⌦',
        'TAB': '⇥',
        'ESCAPE': '×',
        'PAUSE': '⏸',
        'INSERT': 'Ｉ',
        'MENU': '☰',
        'HELP': '‽',
        'CAPSLOCK': '⇪',
        'DIVIDE': '÷',

        'CTRL': '⌃',
        'SHIFT': '⇧',
        'COMMAND': '⌘',
        'OPTION': '⌥',
        'WINDOWS': '⊞',
        'META': '⌃',
        'ALT': 'Ａ',

        'ADD': '+',
        'SUBTRACT': '-',
        'MULTIPLY': '×',
        'EQUAL': '=',
        'SEPARATOR': ' ',
        'DECIMAL': ',',

        'HOME': '⇱',
        'END': '⇲',
        'PAGEUP': '⇑',
        'PAGEDOWN': '⇓',
        'PAGE_UP': '⇑',
        'PAGE_DOWN': '⇓',

        'LEFT': '←',
        'UP': '↑',
        'DOWN': '↓',
        'RIGHT': '→',
    }

    LABELS = {
        **NAMES,
        'SPACE': 'Space',
        'ENTER': 'Enter',
        'RETURN': 'Return',
        'BACKSPACE': 'Backspace',
        'DELETE': 'Delete',
        'TAB': 'Tab',
        'ESCAPE': 'Esc',
        'PAUSE': 'Pause',
        'INSERT': 'Insert',
        'MENU': 'Menu',
        'HELP': 'Help',
        'CAPSLOCK': 'Caps Lock',

        'CTRL': 'Ctrl',
        'SHIFT': 'Shift',
        'COMMAND': 'Command',
        'OPTION': 'Option',
        'WINDOWS': 'Windows',
        'ALT': 'Alt',

        'SEPARATOR': 'Separator',

        'HOME': 'Home',
        'END': 'End',
        'PAGEUP': 'Page Up',
        'PAGEDOWN': 'Page Down',
        'PAGE_UP': 'Page Up',
        'PAGE_DOWN': 'Page Down',
        'SCROLLLOCK': 'Scroll Lock',
    }

    print('key_symbols = {')
    symbols = [k for k in dir(key) if k.isupper()]
    symbols.extend('_{}'.format(n) for n in range(10))
    for name in symbols:
        if name.startswith(('MOTION_', 'MOD_')):
            continue
        value = getattr(key, name)
        note = ''
        if name in NAMES:
            symbol = NAMES[name]
            label = LABELS[name]
        elif name.startswith('L') and name[1:] in NAMES:
            symbol = NAMES[name[1:]]
            label = 'Left ' + LABELS[name[1:]]
        elif name.startswith('R') and name[1:] in NAMES:
            symbol = NAMES[name[1:]]
            label = 'Right ' + LABELS[name[1:]]
        elif name.startswith('NUM_') and name[4:] in NAMES:
            symbol = NAMES[name[4:]]
            label = 'Numpad ' + LABELS[name[4:]]
        elif name.startswith('NUM_') and name[4:].isnumeric():
            symbol = 'n ' + name[4:]
            label = 'Numpad ' + name[4:]
        elif name.startswith('F') and name[1:].isnumeric():
            symbol = label = name
        elif len(name) == 1:
            symbol = label = name
        elif ord(' ') < value <= ord('~'):
            symbol = label = chr(value)
        else:
            if name.startswith('NUM_'):
                symbol = 'n' + name[4:6].lower()
                label = name
            else:
                symbol = name[:3].lower()
                label = name.title()
            note = '            # ? ' + name.lower()
        if name in LABELS:
            label = LABELS[name]
        print('    key.{}: {},{}'.format(
                name,
                repr((symbol, label)),
                note,
            ))
    print('}')

####
key_symbols = {
    key.A: ('A', 'A'),
    key.AMPERSAND: ('&', '&'),
    key.APOSTROPHE: ("'", "'"),
    key.ASCIICIRCUM: ('^', '^'),
    key.ASCIITILDE: ('~', '~'),
    key.ASTERISK: ('*', '*'),
    key.AT: ('@', '@'),
    key.B: ('B', 'B'),
    key.BACKSLASH: ('\\', '\\'),
    key.BACKSPACE: ('⌫', 'Backspace'),
    key.BAR: ('|', '|'),
    key.BEGIN: ('beg', 'Begin'),            # ? begin
    key.BRACELEFT: ('{', '{'),
    key.BRACERIGHT: ('}', '}'),
    key.BRACKETLEFT: ('[', '['),
    key.BRACKETRIGHT: (']', ']'),
    key.BREAK: ('bre', 'Break'),            # ? break
    key.C: ('C', 'C'),
    key.CANCEL: ('can', 'Cancel'),            # ? cancel
    key.CAPSLOCK: ('⇪', 'Caps Lock'),
    key.CLEAR: ('cle', 'Clear'),            # ? clear
    key.COLON: (':', ':'),
    key.COMMA: (',', ','),
    key.D: ('D', 'D'),
    key.DELETE: ('⌦', 'Delete'),
    key.DOLLAR: ('$', '$'),
    key.DOUBLEQUOTE: ('"', '"'),
    key.DOWN: ('↓', '↓'),
    key.E: ('E', 'E'),
    key.END: ('⇲', 'End'),
    key.ENTER: ('⏎', 'Enter'),
    key.EQUAL: ('=', '='),
    key.ESCAPE: ('×', 'Esc'),
    key.EXCLAMATION: ('!', '!'),
    key.EXECUTE: ('exe', 'Execute'),            # ? execute
    key.F: ('F', 'F'),
    key.F1: ('F1', 'F1'),
    key.F10: ('F10', 'F10'),
    key.F11: ('F11', 'F11'),
    key.F12: ('F12', 'F12'),
    key.F13: ('F13', 'F13'),
    key.F14: ('F14', 'F14'),
    key.F15: ('F15', 'F15'),
    key.F16: ('F16', 'F16'),
    key.F17: ('F17', 'F17'),
    key.F18: ('F18', 'F18'),
    key.F19: ('F19', 'F19'),
    key.F2: ('F2', 'F2'),
    key.F20: ('F20', 'F20'),
    key.F3: ('F3', 'F3'),
    key.F4: ('F4', 'F4'),
    key.F5: ('F5', 'F5'),
    key.F6: ('F6', 'F6'),
    key.F7: ('F7', 'F7'),
    key.F8: ('F8', 'F8'),
    key.F9: ('F9', 'F9'),
    key.FIND: ('fin', 'Find'),            # ? find
    key.FUNCTION: ('fun', 'Function'),            # ? function
    key.G: ('G', 'G'),
    key.GRAVE: ('`', '`'),
    key.GREATER: ('>', '>'),
    key.H: ('H', 'H'),
    key.HASH: ('#', '#'),
    key.HELP: ('‽', 'Help'),
    key.HOME: ('⇱', 'Home'),
    key.I: ('I', 'I'),
    key.INSERT: ('Ｉ', 'Insert'),
    key.J: ('J', 'J'),
    key.K: ('K', 'K'),
    key.L: ('L', 'L'),
    key.LALT: ('Ａ', 'Left Alt'),
    key.LCOMMAND: ('⌘', 'Left Command'),
    key.LCTRL: ('⌃', 'Left Ctrl'),
    key.LEFT: ('←', '←'),
    key.LESS: ('<', '<'),
    key.LINEFEED: ('lin', 'Linefeed'),            # ? linefeed
    key.LMETA: ('⌃', 'Left ⌃'),
    key.LOPTION: ('⌥', 'Left Option'),
    key.LSHIFT: ('⇧', 'Left Shift'),
    key.LWINDOWS: ('⊞', 'Left Windows'),
    key.M: ('M', 'M'),
    key.MENU: ('☰', 'Menu'),
    key.MINUS: ('-', '-'),
    key.MODESWITCH: ('mod', 'Modeswitch'),            # ? modeswitch
    key.N: ('N', 'N'),
    key.NUMLOCK: ('num', 'Numlock'),            # ? numlock
    key.NUM_0: ('n 0', 'Numpad 0'),
    key.NUM_1: ('n 1', 'Numpad 1'),
    key.NUM_2: ('n 2', 'Numpad 2'),
    key.NUM_3: ('n 3', 'Numpad 3'),
    key.NUM_4: ('n 4', 'Numpad 4'),
    key.NUM_5: ('n 5', 'Numpad 5'),
    key.NUM_6: ('n 6', 'Numpad 6'),
    key.NUM_7: ('n 7', 'Numpad 7'),
    key.NUM_8: ('n 8', 'Numpad 8'),
    key.NUM_9: ('n 9', 'Numpad 9'),
    key.NUM_ADD: ('+', 'Numpad +'),
    key.NUM_BEGIN: ('nbe', 'NUM_BEGIN'),            # ? num_begin
    key.NUM_DECIMAL: (',', 'Numpad ,'),
    key.NUM_DELETE: ('⌦', 'Numpad Delete'),
    key.NUM_DIVIDE: ('÷', 'Numpad ÷'),
    key.NUM_DOWN: ('↓', 'Numpad ↓'),
    key.NUM_END: ('⇲', 'Numpad End'),
    key.NUM_ENTER: ('⏎', 'Numpad Enter'),
    key.NUM_EQUAL: ('=', 'Numpad ='),
    key.NUM_F1: ('nf1', 'NUM_F1'),            # ? num_f1
    key.NUM_F2: ('nf2', 'NUM_F2'),            # ? num_f2
    key.NUM_F3: ('nf3', 'NUM_F3'),            # ? num_f3
    key.NUM_F4: ('nf4', 'NUM_F4'),            # ? num_f4
    key.NUM_HOME: ('⇱', 'Numpad Home'),
    key.NUM_INSERT: ('Ｉ', 'Numpad Insert'),
    key.NUM_LEFT: ('←', 'Numpad ←'),
    key.NUM_MULTIPLY: ('×', 'Numpad ×'),
    key.NUM_NEXT: ('nne', 'NUM_NEXT'),            # ? num_next
    key.NUM_PAGE_DOWN: ('⇓', 'Numpad Page Down'),
    key.NUM_PAGE_UP: ('⇑', 'Numpad Page Up'),
    key.NUM_PRIOR: ('npr', 'NUM_PRIOR'),            # ? num_prior
    key.NUM_RIGHT: ('→', 'Numpad →'),
    key.NUM_SEPARATOR: ('\xa0', 'Numpad Separator'),
    key.NUM_SPACE: ('␣', 'Numpad Space'),
    key.NUM_SUBTRACT: ('-', 'Numpad -'),
    key.NUM_TAB: ('⇥', 'Numpad Tab'),
    key.NUM_UP: ('↑', 'Numpad ↑'),
    key.O: ('O', 'O'),
    key.P: ('P', 'P'),
    key.PAGEDOWN: ('⇓', 'Page Down'),
    key.PAGEUP: ('⇑', 'Page Up'),
    key.PARENLEFT: ('(', '('),
    key.PARENRIGHT: (')', ')'),
    key.PAUSE: ('⏸', 'Pause'),
    key.PERCENT: ('%', '%'),
    key.PERIOD: ('.', '.'),
    key.PLUS: ('+', '+'),
    key.POUND: ('#', '#'),
    key.PRINT: ('pri', 'Print'),            # ? print
    key.Q: ('Q', 'Q'),
    key.QUESTION: ('?', '?'),
    key.QUOTELEFT: ('`', '`'),
    key.R: ('R', 'R'),
    key.RALT: ('Ａ', 'Right Alt'),
    key.RCOMMAND: ('⌘', 'Right Command'),
    key.RCTRL: ('⌃', 'Right Ctrl'),
    key.REDO: ('red', 'Redo'),            # ? redo
    key.RETURN: ('⏎', 'Return'),
    key.RIGHT: ('→', '→'),
    key.RMETA: ('⌃', 'Right ⌃'),
    key.ROPTION: ('⌥', 'Right Option'),
    key.RSHIFT: ('⇧', 'Right Shift'),
    key.RWINDOWS: ('⊞', 'Right Windows'),
    key.S: ('S', 'S'),
    key.SCRIPTSWITCH: ('scr', 'Scriptswitch'),            # ? scriptswitch
    key.SCROLLLOCK: ('scr', 'Scroll Lock'),            # ? scrolllock
    key.SELECT: ('sel', 'Select'),            # ? select
    key.SEMICOLON: (';', ';'),
    key.SLASH: ('/', '/'),
    key.SPACE: ('␣', 'Space'),
    key.SYSREQ: ('sys', 'Sysreq'),            # ? sysreq
    key.T: ('T', 'T'),
    key.TAB: ('⇥', 'Tab'),
    key.U: ('U', 'U'),
    key.UNDERSCORE: ('_', '_'),
    key.UNDO: ('und', 'Undo'),            # ? undo
    key.UP: ('↑', '↑'),
    key.V: ('V', 'V'),
    key.W: ('W', 'W'),
    key.X: ('X', 'X'),
    key.Y: ('Y', 'Y'),
    key.Z: ('Z', 'Z'),
    key._0: ('0', '0'),
    key._1: ('1', '1'),
    key._2: ('2', '2'),
    key._3: ('3', '3'),
    key._4: ('4', '4'),
    key._5: ('5', '5'),
    key._6: ('6', '6'),
    key._7: ('7', '7'),
    key._8: ('8', '8'),
    key._9: ('9', '9'),
}
