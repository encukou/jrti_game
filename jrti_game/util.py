from pyglet import gl

def clamp(value, minimum=0, maximum=1):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


class reify:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value


def draw_rect(w, h):
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(0, 0)
    gl.glVertex2f(0, h)
    gl.glVertex2f(w, h)
    gl.glVertex2f(w, 0)
    gl.glVertex2f(0, 0)
    gl.glEnd()

def interp(a, b, t):
    t = clamp(t, 0, 1)
    return a * (1-t) + b * t
