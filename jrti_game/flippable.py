from attr import attrs, attrib

from jrti_game.data import spritesheet_texture, spritesheet_data
from jrti_game.data import RED


@attrs()
class Flippable:
    x = attrib(0)
    y = attrib(0)
    width = attrib(8)
    height = attrib(8)

    def draw(self):
        ...


@attrs()
class Sprite(Flippable):
    u = attrib(0)
    v = attrib(0)
    texture_width = attrib()
    texture_height = attrib()

    @texture_width.default
    def _default(self):
        return self.width

    @texture_height.default
    def _default(self):
        return self.height

    def draw(self):
        try:
            texture = self.texture
        except AttributeError:
            texture = spritesheet_texture.get_region(
                self.u, self.v, self.texture_width, self.texture_height)
            self.texture = texture

        texture.blit(self.x, self.y, width=self.width, height=self.height)

class Letter(Sprite):
    def __init__(self, letter, **kwargs):
        number = ord(letter)
        if ord('a') <= number <= ord('z'):
            u = 8 * (number - ord('a'))
            v = 0
        elif ord('A') <= number <= ord('Z'):
            u = 8 * (number - ord('A'))
            v = 8
        else:
            u = 0
            v = 8 * 2
        for width in range(8, 0, -1):
            if spritesheet_data[v+7][u+width-1] != RED:
                break
        kwargs.update(
            texture_width=width,
            texture_height=8,
            u=u,
            v=v,
        )
        if 'width' not in kwargs:
            kwargs['width'] = (kwargs['height'] // 8 * width) or 1
        print(kwargs)
        super().__init__(**kwargs)
