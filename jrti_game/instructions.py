import sys
import traceback

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
            if name == 'end_time':
                if state.end_time is None:
                    return 'some cheaty way'
                else:
                    return format_end_time(state.end_time)
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


def format_end_time(time):
    def s(val, text):
        return "{val} {text}{s}".format(val=val, text=text,
                                        s='' if val==1 else 's')

    time = int(time)

    if time == 0:
        return 'some cheaty way'

    result = []
    for number, unit in (
            (60, 'second'),
            (60, 'minute'),
            (24, 'hour'),
            (7, 'day'),
    ):
        time, val = divmod(time, number)
        if val:
            result.append(s(val, unit))
    if time:
        result.append(s(time, 'week'))

    result.reverse()
    result[-2:] = [' and '.join(result[-2:])]
    return ', '.join(result)


def test_eq(a, b):
    if a != b:
        print('Fail:')
        print('    got:', repr(a))
        print('    exp:', repr(b))

test_eq(format_end_time(0), 'some cheaty way')
test_eq(format_end_time(1), '1 second')
test_eq(format_end_time(2), '2 seconds')
test_eq(format_end_time(60), '1 minute')
test_eq(format_end_time(62), '1 minute and 2 seconds')
test_eq(format_end_time(3600), '1 hour')
test_eq(format_end_time(3663), '1 hour, 1 minute and 3 seconds')
test_eq(format_end_time(3600*24), '1 day')
test_eq(format_end_time(3601*24), '1 day and 24 seconds')
test_eq(format_end_time(3600*24*7), '1 week')
test_eq(format_end_time(3600*24*7*2), '2 weeks')
test_eq(format_end_time(3600*24*7*2+3600*24*3+3600*7+60*2+3),
        '2 weeks, 3 days, 7 hours, 2 minutes and 3 seconds')
test_eq(format_end_time(3600*24*7*200), '200 weeks')
