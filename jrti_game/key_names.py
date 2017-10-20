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
        'NUM_SEPARATOR': '  ',
        'NUM_DECIMAL': ' ,',

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
        elif name.startswith('L') and name[1:] in NAMES:
            symbol = NAMES[name[1:]] + '  '
        elif name.startswith('R') and name[1:] in NAMES:
            symbol = '  ' + NAMES[name[1:]]
        elif name.startswith('NUM_') and name[4:] in NAMES:
            symbol = ' ' + NAMES[name[4:]]
        elif name.startswith('NUM_') and name[4:].isnumeric():
            symbol = ' ' + name[4:]
        elif name.startswith('F') and name[1:].isnumeric():
            symbol = name
        elif len(name) != 1 and ord(' ') < value <= ord('~'):
            symbol = chr(value)
        elif len(name) == 1:
            symbol = name
        else:
            if name.startswith('NUM_'):
                symbol = 'n' + name[4:6].lower()
            else:
                symbol = name[:3].lower()
            note = '            # ? ' + name.lower()
        print('    key.{}: {},{}'.format(
                name,
                repr(symbol),
                note,
            ))
    print('}')

####
key_symbols = {
    key.A: 'A',
    key.AMPERSAND: '&',
    key.APOSTROPHE: "'",
    key.ASCIICIRCUM: '^',
    key.ASCIITILDE: '~',
    key.ASTERISK: '*',
    key.AT: '@',
    key.B: 'B',
    key.BACKSLASH: '\\',
    key.BACKSPACE: '⌫',
    key.BAR: '|',
    key.BEGIN: 'beg',            # ? begin
    key.BRACELEFT: '{',
    key.BRACERIGHT: '}',
    key.BRACKETLEFT: '[',
    key.BRACKETRIGHT: ']',
    key.BREAK: 'bre',            # ? break
    key.C: 'C',
    key.CANCEL: 'can',            # ? cancel
    key.CAPSLOCK: '⇪',
    key.CLEAR: 'cle',            # ? clear
    key.COLON: ':',
    key.COMMA: ',',
    key.D: 'D',
    key.DELETE: '⌦',
    key.DOLLAR: '$',
    key.DOUBLEQUOTE: '"',
    key.DOWN: '↓',
    key.E: 'E',
    key.END: '⇲',
    key.ENTER: '⏎',
    key.EQUAL: '=',
    key.ESCAPE: '×',
    key.EXCLAMATION: '!',
    key.EXECUTE: 'exe',            # ? execute
    key.F: 'F',
    key.F1: 'F1',
    key.F10: 'F10',
    key.F11: 'F11',
    key.F12: 'F12',
    key.F13: 'F13',
    key.F14: 'F14',
    key.F15: 'F15',
    key.F16: 'F16',
    key.F17: 'F17',
    key.F18: 'F18',
    key.F19: 'F19',
    key.F2: 'F2',
    key.F20: 'F20',
    key.F3: 'F3',
    key.F4: 'F4',
    key.F5: 'F5',
    key.F6: 'F6',
    key.F7: 'F7',
    key.F8: 'F8',
    key.F9: 'F9',
    key.FIND: 'fin',            # ? find
    key.FUNCTION: 'fun',            # ? function
    key.G: 'G',
    key.GRAVE: '`',
    key.GREATER: '>',
    key.H: 'H',
    key.HASH: '#',
    key.HELP: '‽',
    key.HOME: '⇱',
    key.I: 'I',
    key.INSERT: 'Ｉ',
    key.J: 'J',
    key.K: 'K',
    key.L: 'L',
    key.LALT: 'Ａ  ',
    key.LCOMMAND: '⌘  ',
    key.LCTRL: '⌃  ',
    key.LEFT: '←',
    key.LESS: '<',
    key.LINEFEED: 'lin',            # ? linefeed
    key.LMETA: '⌃  ',
    key.LOPTION: '⌥  ',
    key.LSHIFT: '⇧  ',
    key.LWINDOWS: '⊞  ',
    key.M: 'M',
    key.MENU: '☰',
    key.MINUS: '-',
    key.MODESWITCH: 'mod',            # ? modeswitch
    key.N: 'N',
    key.NUMLOCK: 'num',            # ? numlock
    key.NUM_0: ' 0',
    key.NUM_1: ' 1',
    key.NUM_2: ' 2',
    key.NUM_3: ' 3',
    key.NUM_4: ' 4',
    key.NUM_5: ' 5',
    key.NUM_6: ' 6',
    key.NUM_7: ' 7',
    key.NUM_8: ' 8',
    key.NUM_9: ' 9',
    key.NUM_ADD: ' +',
    key.NUM_BEGIN: 'nbe',            # ? num_begin
    key.NUM_DECIMAL: ' ,',
    key.NUM_DELETE: ' ⌦',
    key.NUM_DIVIDE: ' ÷',
    key.NUM_DOWN: ' ↓',
    key.NUM_END: ' ⇲',
    key.NUM_ENTER: ' ⏎',
    key.NUM_EQUAL: ' =',
    key.NUM_F1: 'nf1',            # ? num_f1
    key.NUM_F2: 'nf2',            # ? num_f2
    key.NUM_F3: 'nf3',            # ? num_f3
    key.NUM_F4: 'nf4',            # ? num_f4
    key.NUM_HOME: ' ⇱',
    key.NUM_INSERT: ' Ｉ',
    key.NUM_LEFT: ' ←',
    key.NUM_MULTIPLY: ' ×',
    key.NUM_NEXT: 'nne',            # ? num_next
    key.NUM_PAGE_DOWN: ' ⇓',
    key.NUM_PAGE_UP: ' ⇑',
    key.NUM_PRIOR: 'npr',            # ? num_prior
    key.NUM_RIGHT: ' →',
    key.NUM_SEPARATOR: ' \xa0',
    key.NUM_SPACE: ' ␣',
    key.NUM_SUBTRACT: ' -',
    key.NUM_TAB: ' ⇥',
    key.NUM_UP: ' ↑',
    key.O: 'O',
    key.P: 'P',
    key.PAGEDOWN: '⇓',
    key.PAGEUP: '⇑',
    key.PARENLEFT: '(',
    key.PARENRIGHT: ')',
    key.PAUSE: '⏸',
    key.PERCENT: '%',
    key.PERIOD: '.',
    key.PLUS: '+',
    key.POUND: '#',
    key.PRINT: 'pri',            # ? print
    key.Q: 'Q',
    key.QUESTION: '?',
    key.QUOTELEFT: '`',
    key.R: 'R',
    key.RALT: '  Ａ',
    key.RCOMMAND: '  ⌘',
    key.RCTRL: '  ⌃',
    key.REDO: 'red',            # ? redo
    key.RETURN: '⏎',
    key.RIGHT: '→',
    key.RMETA: '  ⌃',
    key.ROPTION: '  ⌥',
    key.RSHIFT: '  ⇧',
    key.RWINDOWS: '  ⊞',
    key.S: 'S',
    key.SCRIPTSWITCH: 'scr',            # ? scriptswitch
    key.SCROLLLOCK: 'scr',            # ? scrolllock
    key.SELECT: 'sel',            # ? select
    key.SEMICOLON: ';',
    key.SLASH: '/',
    key.SPACE: '␣',
    key.SYSREQ: 'sys',            # ? sysreq
    key.T: 'T',
    key.TAB: '⇥',
    key.U: 'U',
    key.UNDERSCORE: '_',
    key.UNDO: 'und',            # ? undo
    key.UP: '↑',
    key.V: 'V',
    key.W: 'W',
    key.X: 'X',
    key.Y: 'Y',
    key.Z: 'Z',
    key._0: '0',
    key._1: '1',
    key._2: '2',
    key._3: '3',
    key._4: '4',
    key._5: '5',
    key._6: '6',
    key._7: '7',
    key._8: '8',
    key._9: '9',
}
