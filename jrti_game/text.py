import functools
import contextlib

from pyglet import gl

from jrti_game.data import spritesheet_data, spritesheet_texture, sprites
from jrti_game.flippable import Sprite
from jrti_game.key_names import key_symbols
from jrti_game.util import draw_rect, draw_rect_xy, clamp, draw_keyhole
from jrti_game.state import state


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

    def draw(self, zoom, **kwargs):
        super().draw(zoom=zoom, **kwargs)
        if self.keyhole and zoom > 9:
            gl.glColor4f(*self.bgcolor)
            draw_keyhole(self.keyhole)


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


@contextlib.contextmanager
def draw_opening(self):
    gl.glPushMatrix()
    draw_rect_xy(*self.innards)
    gl.glColor3f(1, 1, 1)
    draw_rect_xy(*self.innards, mode=gl.GL_LINE_STRIP, last=False)
    gl.glPushMatrix()
    yield
    gl.glPopMatrix()
    right = self.innards[0] + self.innards[2]
    gl.glTranslatef(right, 0, 0)
    t = clamp((state.time - self.unlocked.open_anim_start)*2, 0, 1)**3
    gl.glRotatef(-t*100, 0, 1, 0)
    gl.glTranslatef(-right, 0, 0)
    gl.glColor3f(1, 1, 1)
    draw_rect_xy(*self.innards)
    gl.glColor4f(0, 0, 0, 1/2)
    draw_rect_xy(*self.innards, mode=gl.GL_LINE_STRIP, last=False)
    gl.glPopMatrix()


class Eye(Letter):
    keyhole = 2-1/16, 7, 1/16, 1
    innards = 2+1/8, 7+1/16, 2-3/16, 1-2/16

    def draw(self, zoom, **kwargs):
        super().draw(zoom=zoom, children=False, **kwargs)
        if self.unlocked:
            if zoom > 4:
                gl.glColor3f(0, 0, 0)
            else:
                gl.glColor3f(1, 1, 1)
            with draw_opening(self):
                if zoom > 4:
                    for child in self.children:
                        child.draw_outer(zoom=zoom*child.scale, **kwargs)

                gl.glPushMatrix()
                gl.glColor3f(1, 1, 1)
                x, y, z = self.unlocked.obj_pos
                gl.glTranslatef(x, y, 0)
                gl.glScalef(1/64, 1/64, 0)
                for i, num in enumerate(state.key_config):
                    draw_string(str(int(num)), x=i*14/32*64+12, y=-5)
                gl.glPopMatrix()


    def unlock(self, key):
        from jrti_game.adjuster import Adjuster
        super().unlock(key)
        for i in range(4):
            a = Adjuster(
                parent=self,
                x=2+3/8+i*14/32,
                y=7+6/64,
                scale=1/128,
                width=24,
                height=80+24,
                instructions='Adjusting',
            )
            a.index = i


class Exclamation(Letter):
    keyhole = 1, 2.25, 2/32, 1/2
    innards = 1+1/8, 1+1/16, 2-3/16, 2-2/16

    def draw(self, zoom, **kwargs):
        super().draw(zoom=zoom, **kwargs)
        if self.unlocked:
            gl.glColor3f(0.1, 0.2, 0.5)
            with draw_opening(self):
                gl.glTranslatef(1, 1, 0)
                gl.glScalef(1/8, 1/8, 1)
                gl.glColor3f(0.4, 1, 0.2)
                sprites['eye_big'].blit(1.75, 1.5)


class Dot(Letter):
    keyhole = 1, 2.25, 2/32, 1/2
    innards = 1+1/8, 1+1/16, 2-3/16, 2-2/16

    def draw(self, zoom, **kwargs):
        super().draw(zoom=zoom, **kwargs)
        if self.unlocked:
            gl.glColor3f(0.1, 0.2, 0.5)
            with draw_opening(self):
                gl.glTranslatef(1, 1, 0)
                gl.glScalef(1/8, 1/8, 1)
                gl.glColor3f(0.4, 1, 0.2)
                sprites['bug_o'].blit(1.75, 1.5)


class Colon(Letter):
    keyhole = 1, 6.25, 2/32, 1/2
    innards = 1+1/8, 2+1/16, 2-3/16, 2-2/16

    def draw(self, zoom, **kwargs):
        super().draw(zoom=zoom, **kwargs)
        if self.unlocked:
            gl.glColor3f(0.1, 0.2, 0.5)
            with draw_opening(self):
                gl.glTranslatef(1, 2, 0)
                gl.glScalef(1/8, 1/8, 1)
                gl.glColor3f(0.4, 1, 0.2)
                sprites['hint_a'].blit(1.75, 1.5)

            gl.glTranslatef(0, 3, 0)
            gl.glColor3f(0.1, 0.2, 0.5)
            with draw_opening(self):
                gl.glTranslatef(1, 2, 0)
                gl.glScalef(1/8, 1/8, 1)
                gl.glColor3f(0.4, 1, 0.2)
                sprites['hint_b'].blit(1.75, 1.5)
            gl.glTranslatef(0, -3, 0)


SPECIAL_LETTER_CLASSES = {
    'i': Eye,
    'o': Oh,
    '!': Exclamation,
    '.': Dot,
    ':': Colon,
}
