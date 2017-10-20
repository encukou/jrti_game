import sys
import traceback

import pyglet

from jrti_game.data import load_instructions, default_keymap
from jrti_game.state import state
from jrti_game.key_names import key_symbols


instruction_texts = load_instructions()


def get_instruction_text(key):
    text = instruction_texts.get(key, instruction_texts['None'])
    return text.format_map(substitutions)


class Substitutions(dict):
    def __missing__(self, name):
        try:
            if name == 'state':
                return state
            action = default_keymap.get(name)
            if action:
                for current_key, current_action in state.keymap.items():
                    if current_action == action:
                        try:
                            return key_symbols[current_key][1]
                        except KeyError:
                            return 'Key {0:x}'.format(current_key)
                return '?'

            raise LookupError()
        except:
            traceback.print_exc()
            print(file=sys.stderr)
            raise


substitutions = Substitutions()
