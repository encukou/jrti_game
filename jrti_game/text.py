import functools

from pyglet import gl

from jrti_game.data import spritesheet_data, spritesheet_texture
from jrti_game.flippable import Sprite
from jrti_game.key_names import key_symbols
from jrti_game.util import draw_rect


@functools.lru_cache()
def letter_uvwh(character):
    number = specials.get(character, ord(character))
    if number < ord(' '):
        number = 127
    if number > 0xff:
        number = 127
    u = 8 * ((number - ord(' ')) % 32)
    v = 8 * ((number - ord(' ')) // 32)
    for width in range(8, 0, -1):
        if any(spritesheet_data[v+7-i][u+width-1]
               for i in range(8)):
            break
    return u, v, width+1, 9


def text_width(string):
    width = 0
    last_char = None
    for character in string:
        u, v, w, h = letter_uvwh(character)
        width += w + kerns.get((last_char, character), 0)
    return width


specials = {
    '␣': 0x90,
    '⏎': 0x91,
    '⌫': 0x92,
    '⌦': 0x93,
    '⇥': 0x94,
    '×': 0x95,
    '⏸': 0x96,
    'Ｉ': 0x97,
    '☰': 0x98,
    '‽': 0x99,
    '⇪': 0x9a,

    '⌃': 0x9b,
    '⇧': 0x9c,
    '⌘': 0x9d,
    '⌥': 0x9e,
    '⊞': 0x9f,
    'Ａ': 0xb0,

    '⇱': 0xb1,
    '⇲': 0xb2,
    '⇑': 0xb3,
    '⇓': 0xb4,

    '←': 0xb5,
    '↑': 0xb6,
    '↓': 0xb7,
    '→': 0xb8,

    '⌀': 0xb9,
    '÷': 0xba
}

kerns = {
    ('s', 't'): -1,
    ('/', '/'): -1,
}


def draw_string(string, center=False, hcenter=False, x=0, y=0):
    if center:
        x -= (text_width(string)-1) / 2
    if hcenter:
        y -= 4
    for char in string:
        u, v, w, h = letter_uvwh(char)
        if char != ' ':
            spritesheet_texture.get_region(u, v, w, h).blit(x, y)
        x += w


def draw_key(key, x=0, y=0):
    if key in key_symbols:
        txt = key_symbols[key][0]
        draw_string(txt, center=True, hcenter=True, x=x, y=y)
    else:
        gl.glPushMatrix()
        gl.glScalef(1/4, 1/4, 1)
        txt = '{0:016x}'.format(key).replace('0', '⌀')
        draw_string(txt[-16:-12], center=True, hcenter=True, x=x, y=y+12)
        draw_string(txt[-12:-8], center=True, hcenter=True, x=x, y=y+4)
        draw_string(txt[-8:-4], center=True, hcenter=True, x=x, y=y-4)
        draw_string(txt[-4:], center=True, hcenter=True, x=x, y=y+-12)
        gl.glPopMatrix()


class Letter(Sprite):
    def __init__(self, letter, strim=0, etrim=0, **kwargs):
        u, v, width, height = letter_uvwh(letter)
        width += 1-etrim-strim
        kwargs.update(
            texture_width=width,
            texture_height=height,
            u=u-1+strim,
            v=v,
        )
        if 'width' not in kwargs:
            kwargs['width'] = (kwargs['height'] // 9 * width) or 1
        kwargs.setdefault('instructions', letter.upper())
        kwargs.setdefault('margin', 1/2)
        super().__init__(**kwargs)


def letters(string, x=0, y=0, scale=1, center=False, parent=None,
            replace=None):
    if center:
        x -= scale * (text_width(string) // 2)
    starting_x = x
    next_kern = 0
    for character, next_char in zip(string, string[1:] + ' '):
        instructions = character.upper()
        if character == '\n':
            y -= scale * 8
            x = starting_x
        else:
            x += next_kern
            if next_kern < 0:
                strim = 1
                x += scale
            else:
                strim = 0
            next_kern = kerns.get((character, next_char), 0) * scale
            if next_kern < 0:
                etrim = 1
            else:
                etrim = 0
            if character == ' ':
                x += (4 + etrim) * scale
            else:
                cls = SPECIAL_LETTER_CLASSES.get(character, Letter)
                letter = cls(character, x=x, y=y, height=9, scale=scale,
                             strim=strim, etrim=etrim, parent=parent,
                             instructions=instructions)
                x += (letter.width + etrim) * scale - scale
                yield letter


class Oh(Letter):
    def draw(self, **kwargs):
        super().draw(**kwargs)
        gl.glPushMatrix()
        gl.glColor4f(*self.bgcolor)
        gl.glTranslatef(3, 2, 0)
        draw_rect(1, 4)
        gl.glPopMatrix()


class Eye(Letter):
    keyhole = 2, 7.25, 2/32, 1/2


class Exclamation(Letter):
    keyhole = 1, 2.25, 2/32, 1/2


class Dot(Letter):
    keyhole = 1, 2.25, 2/32, 1/2

SPECIAL_LETTER_CLASSES = {'i': Eye, 'o': Oh, '!': Exclamation, '.': Dot}
